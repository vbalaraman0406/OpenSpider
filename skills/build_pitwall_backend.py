import os

BASE = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Wrote {full}')

# 1. data/__init__.py
w('data/__init__.py', '# Data module\n')

# 2. routers/__init__.py
w('routers/__init__.py', '# Routers module\n')

# 3. data/fastf1_loader.py
w('data/fastf1_loader.py', '''"""FastF1 Data Loader Module for Pitwall.ai

Provides functions to load and extract F1 session data using the fastf1 library.
All data is cached locally for performance.
"""

import os
import logging
from typing import Optional

import fastf1
import pandas as pd

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def get_event_schedule(year: int) -> pd.DataFrame:
    """Get the full event schedule for a given season."""
    try:
        schedule = fastf1.get_event_schedule(year)
        schedule = schedule[schedule["RoundNumber"] > 0]
        return schedule
    except Exception as e:
        logger.error("Failed to load event schedule for %d: %s", year, e)
        raise


def _load_session(year: int, round_number: int, session_type: str) -> fastf1.core.Session:
    """Internal helper to load and return a fastf1 Session object."""
    session = fastf1.get_session(year, round_number, session_type)
    session.load(telemetry=True, laps=True, weather=False, messages=False)
    return session


def get_session_results(year: int, round_number: int, session_type: str = "R") -> pd.DataFrame:
    """Get session classification / results."""
    try:
        session = _load_session(year, round_number, session_type)
        results = session.results
        if results is None or results.empty:
            return pd.DataFrame()
        cols = ["DriverNumber", "BroadcastName", "Abbreviation", "TeamName",
                "Position", "ClassifiedPosition", "GridPosition",
                "Time", "Status", "Points"]
        available = [c for c in cols if c in results.columns]
        return results[available].reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load session results: %s", e)
        raise


def get_lap_data(year: int, round_number: int, session_type: str = "R",
                 driver: Optional[str] = None) -> pd.DataFrame:
    """Get lap-by-lap timing data."""
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps
        if laps is None or laps.empty:
            return pd.DataFrame()
        if driver:
            laps = laps.pick_drivers(driver)
        cols = ["Driver", "DriverNumber", "LapNumber", "LapTime",
                "Sector1Time", "Sector2Time", "Sector3Time",
                "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST",
                "Compound", "TyreLife", "FreshTyre", "Stint", "IsPersonalBest"]
        available = [c for c in cols if c in laps.columns]
        df = laps[available].copy()
        for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
            if col in df.columns:
                df[col] = df[col].dt.total_seconds()
        return df.reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load lap data: %s", e)
        raise


def get_telemetry(year: int, round_number: int, driver: str,
                  session_type: str = "R", lap_number: Optional[int] = None) -> pd.DataFrame:
    """Get car telemetry for a specific driver."""
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            return pd.DataFrame()
        if lap_number is not None:
            lap = laps[laps["LapNumber"] == lap_number]
            if lap.empty:
                return pd.DataFrame()
            lap = lap.iloc[0]
        else:
            lap = laps.pick_fastest()
        telemetry = lap.get_telemetry()
        if telemetry is None or telemetry.empty:
            return pd.DataFrame()
        cols = ["Distance", "Speed", "Throttle", "Brake", "nGear", "RPM", "DRS", "X", "Y", "Z"]
        available = [c for c in cols if c in telemetry.columns]
        return telemetry[available].reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load telemetry for %s: %s", driver, e)
        raise


def get_tire_strategy(year: int, round_number: int, session_type: str = "R") -> pd.DataFrame:
    """Get tire strategy data for all drivers in a session."""
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps
        if laps is None or laps.empty:
            return pd.DataFrame()
        stints = (laps.groupby(["Driver", "Stint", "Compound"])
                  .agg(StintStartLap=("LapNumber", "min"),
                       StintEndLap=("LapNumber", "max"),
                       TotalLaps=("LapNumber", "count"))
                  .reset_index())
        return stints.sort_values(["Driver", "Stint"]).reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load tire strategy: %s", e)
        raise


def get_race_results(year: int, round_number: int) -> pd.DataFrame:
    """Convenience wrapper for race classification."""
    return get_session_results(year, round_number, session_type="R")


def get_driver_season_stats(year: int, driver: str) -> dict:
    """Aggregate season statistics for a single driver."""
    try:
        schedule = get_event_schedule(year)
        stats = {"driver": driver, "year": year, "races": 0, "wins": 0,
                 "podiums": 0, "poles": 0, "points": 0.0, "avg_finish": 0.0,
                 "avg_grid": 0.0, "dnfs": 0, "fastest_laps": 0}
        finishes, grids = [], []
        for _, event in schedule.iterrows():
            rnd = int(event["RoundNumber"])
            try:
                results = get_session_results(year, rnd, "R")
            except Exception:
                continue
            if results.empty:
                continue
            drv = results[results["Abbreviation"] == driver]
            if drv.empty:
                continue
            row = drv.iloc[0]
            stats["races"] += 1
            pos = row.get("Position")
            grid = row.get("GridPosition")
            pts = row.get("Points", 0)
            status = str(row.get("Status", ""))
            if pos is not None and not pd.isna(pos):
                pos = int(pos)
                finishes.append(pos)
                if pos == 1: stats["wins"] += 1
                if pos <= 3: stats["podiums"] += 1
            if grid is not None and not pd.isna(grid):
                grids.append(int(grid))
                if int(grid) == 1: stats["poles"] += 1
            stats["points"] += float(pts) if pts and not pd.isna(pts) else 0.0
            if "Finished" not in status and "+" not in status:
                stats["dnfs"] += 1
        if finishes:
            stats["avg_finish"] = round(sum(finishes) / len(finishes), 2)
        if grids:
            stats["avg_grid"] = round(sum(grids) / len(grids), 2)
        return stats
    except Exception as e:
        logger.error("Failed to compute season stats for %s: %s", driver, e)
        raise


def get_drivers_comparison(year: int, drivers: list) -> list:
    """Compare multiple drivers season stats side by side."""
    return [get_driver_season_stats(year, d) for d in drivers]
''')

# 4. data/models.py
w('data/models.py', '''"""Pydantic models for Pitwall.ai API responses."""

from typing import Optional, List
from pydantic import BaseModel


class RaceResult(BaseModel):
    position: int
    driver_number: str
    driver_name: str
    driver_code: str
    team: str
    grid_position: int
    time: Optional[str] = None
    status: str
    points: float


class DriverLap(BaseModel):
    driver: str
    driver_number: Optional[str] = None
    lap_number: int
    lap_time: Optional[float] = None
    sector1: Optional[float] = None
    sector2: Optional[float] = None
    sector3: Optional[float] = None
    speed_i1: Optional[float] = None
    speed_i2: Optional[float] = None
    speed_fl: Optional[float] = None
    speed_st: Optional[float] = None
    compound: Optional[str] = None
    tyre_life: Optional[int] = None
    fresh_tyre: Optional[bool] = None
    stint: Optional[int] = None
    is_personal_best: Optional[bool] = None


class TelemetryPoint(BaseModel):
    distance: float
    speed: float
    throttle: float
    brake: float
    gear: int
    rpm: Optional[int] = None
    drs: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class TireStrategy(BaseModel):
    driver: str
    stint: int
    compound: str
    stint_start_lap: int
    stint_end_lap: int
    total_laps: int


class SessionSummary(BaseModel):
    year: int
    round_number: int
    event_name: str
    country: str
    location: str
    session_type: str
    date: Optional[str] = None


class DriverStats(BaseModel):
    driver: str
    year: int
    races: int
    wins: int
    podiums: int
    poles: int
    points: float
    avg_finish: float
    avg_grid: float
    dnfs: int
    fastest_laps: int


class EventInfo(BaseModel):
    round_number: int
    country: str
    location: str
    event_name: str
    event_date: Optional[str] = None
    event_format: Optional[str] = None


class DriverInfo(BaseModel):
    driver_number: str
    broadcast_name: str
    abbreviation: str
    team_name: str


class ComparisonResponse(BaseModel):
    drivers: List[DriverStats]
''')

# 5. routers/race.py
w('routers/race.py', '''"""Race data API routes for Pitwall.ai."""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from data.fastf1_loader import (
    get_event_schedule,
    get_session_results,
    get_lap_data,
    get_telemetry,
    get_tire_strategy,
)

router = APIRouter(prefix="/api/races", tags=["races"])


@router.get("/{year}")
async def list_races(year: int):
    """List all races in a season."""
    try:
        schedule = get_event_schedule(year)
        events = []
        for _, row in schedule.iterrows():
            events.append({
                "round_number": int(row["RoundNumber"]),
                "country": str(row.get("Country", "")),
                "location": str(row.get("Location", "")),
                "event_name": str(row.get("OfficialEventName", row.get("EventName", ""))),
                "event_date": str(row.get("EventDate", "")) if row.get("EventDate") is not None else None,
                "event_format": str(row.get("EventFormat", "")),
            })
        return {"year": year, "total_races": len(events), "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/{round_number}/results")
async def race_results(year: int, round_number: int,
                       session: str = Query(default="R", description="Session type: FP1, FP2, FP3, Q, S, R")):
    """Get race/session results."""
    try:
        results = get_session_results(year, round_number, session)
        if results.empty:
            return {"year": year, "round": round_number, "session": session, "results": []}
        records = results.to_dict(orient="records")
        for r in records:
            for k, v in r.items():
                if hasattr(v, "total_seconds"):
                    r[k] = v.total_seconds()
        return {"year": year, "round": round_number, "session": session, "results": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/{round_number}/laps")
async def lap_data(year: int, round_number: int,
                   driver: Optional[str] = Query(default=None, description="Driver code e.g. VER"),
                   session: str = Query(default="R")):
    """Get lap-by-lap timing data."""
    try:
        laps = get_lap_data(year, round_number, session, driver)
        if laps.empty:
            return {"year": year, "round": round_number, "laps": []}
        records = laps.to_dict(orient="records")
        return {"year": year, "round": round_number, "driver": driver, "total_laps": len(records), "laps": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/{round_number}/telemetry/{driver}")
async def driver_telemetry(year: int, round_number: int, driver: str,
                           lap: Optional[int] = Query(default=None, description="Specific lap number"),
                           session: str = Query(default="R")):
    """Get driver telemetry data."""
    try:
        tel = get_telemetry(year, round_number, driver, session, lap)
        if tel.empty:
            return {"year": year, "round": round_number, "driver": driver, "telemetry": []}
        records = tel.to_dict(orient="records")
        return {"year": year, "round": round_number, "driver": driver,
                "lap": lap or "fastest", "data_points": len(records), "telemetry": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/{round_number}/strategy")
async def tire_strategy(year: int, round_number: int,
                        session: str = Query(default="R")):
    """Get tire strategy for all drivers."""
    try:
        strategy = get_tire_strategy(year, round_number, session)
        if strategy.empty:
            return {"year": year, "round": round_number, "strategy": []}
        records = strategy.to_dict(orient="records")
        return {"year": year, "round": round_number, "total_stints": len(records), "strategy": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''')

# 6. routers/drivers.py
w('routers/drivers.py', '''"""Driver data API routes for Pitwall.ai."""

from typing import List
from fastapi import APIRouter, HTTPException, Query

from data.fastf1_loader import (
    get_event_schedule,
    get_session_results,
    get_driver_season_stats,
    get_drivers_comparison,
)

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("/{year}")
async def list_drivers(year: int):
    """List all drivers in a season (from the first available race)."""
    try:
        schedule = get_event_schedule(year)
        for _, event in schedule.iterrows():
            rnd = int(event["RoundNumber"])
            try:
                results = get_session_results(year, rnd, "R")
                if not results.empty:
                    drivers = []
                    for _, row in results.iterrows():
                        drivers.append({
                            "driver_number": str(row.get("DriverNumber", "")),
                            "broadcast_name": str(row.get("BroadcastName", "")),
                            "abbreviation": str(row.get("Abbreviation", "")),
                            "team_name": str(row.get("TeamName", "")),
                        })
                    return {"year": year, "total_drivers": len(drivers), "drivers": drivers}
            except Exception:
                continue
        return {"year": year, "total_drivers": 0, "drivers": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/{driver_code}/stats")
async def driver_stats(year: int, driver_code: str):
    """Get aggregated season stats for a driver."""
    try:
        stats = get_driver_season_stats(year, driver_code.upper())
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{year}/compare")
async def compare_drivers(year: int,
                          drivers: str = Query(..., description="Comma-separated driver codes e.g. VER,LEC,HAM")):
    """Head-to-head comparison of multiple drivers."""
    try:
        driver_list = [d.strip().upper() for d in drivers.split(",") if d.strip()]
        if len(driver_list) < 2:
            raise HTTPException(status_code=400, detail="Provide at least 2 driver codes separated by commas")
        comparison = get_drivers_comparison(year, driver_list)
        return {"year": year, "drivers": comparison}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''')

# 7. main.py
w('main.py', '''"""Pitwall.ai — F1 Analytics API

FastAPI application serving F1 race data, driver stats, and telemetry
powered by the FastF1 library.
"""

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import fastf1

from routers.race import router as race_router
from routers.drivers import router as drivers_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Configure FastF1 cache
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)
logger.info("FastF1 cache directory: %s", CACHE_DIR)

# Create FastAPI app
app = FastAPI(
    title="Pitwall.ai",
    description="F1 Analytics API — Race data, driver stats, telemetry & predictions",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for all origins (frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(race_router)
app.include_router(drivers_router)


@app.get("/")
async def root():
    """Health check / welcome endpoint."""
    return {
        "service": "Pitwall.ai",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "races": "/api/races/{year}",
            "results": "/api/races/{year}/{round}/results",
            "laps": "/api/races/{year}/{round}/laps",
            "telemetry": "/api/races/{year}/{round}/telemetry/{driver}",
            "strategy": "/api/races/{year}/{round}/strategy",
            "drivers": "/api/drivers/{year}",
            "driver_stats": "/api/drivers/{year}/{driver_code}/stats",
            "compare": "/api/drivers/{year}/compare?drivers=VER,LEC",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
''')

# 8. requirements.txt
w('requirements.txt', '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
fastf1>=3.3.0
pandas>=2.0.0
numpy>=1.24.0
pydantic>=2.0.0
scikit-learn>=1.3.0
xgboost>=2.0.0
requests>=2.31.0
''')

# 9. app.yaml (Google App Engine)
w('app.yaml', '''runtime: python312
entrypoint: uvicorn main:app --host 0.0.0.0 --port $PORT

instance_class: F2

automatic_scaling:
  min_instances: 0
  max_instances: 3
  target_cpu_utilization: 0.65

env_variables:
  PYTHONUNBUFFERED: "1"
''')

# 10. .gitignore
w('.gitignore', '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
instance/
.webassets-cache
.scrapy
docs/_build/
target/
.ipynb_checkpoints
profile_default/
ipython_config.py
.pdm.toml
__pypackages__/
celerybeat-schedule
celerybeat.pid
*.sage.py
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.spyderproject
.spyproject
.ropeproject
/site
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
.pytype/
cython_debug/
cache/
*.cache
node_modules/
''')

print('\n=== All backend files written successfully ===')
print(f'Base directory: {BASE}')

# Verify
for root, dirs, files in os.walk(BASE):
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        rel = os.path.relpath(path, BASE)
        print(f'  {rel} ({size} bytes)')
