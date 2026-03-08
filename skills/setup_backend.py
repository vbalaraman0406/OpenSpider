import os

# Use relative path from working directory
base = 'workspace/pitwall-ai/backend'

def w(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Wrote: {full} ({len(content)} bytes)')

# __init__.py files
w('data/__init__.py', '# Data module\n')
w('routers/__init__.py', '# Routers module\n')

# fastf1_loader.py
loader = '''"""FastF1 Data Loader for Pitwall.ai"""
import os, logging
from typing import Optional
import fastf1
import pandas as pd

logger = logging.getLogger(__name__)
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

def get_event_schedule(year):
    schedule = fastf1.get_event_schedule(year)
    return schedule[schedule["RoundNumber"] > 0]

def _load_session(year, rnd, stype):
    session = fastf1.get_session(year, rnd, stype)
    session.load(telemetry=True, laps=True, weather=False, messages=False)
    return session

def get_session_results(year, rnd, stype="R"):
    session = _load_session(year, rnd, stype)
    results = session.results
    if results is None or results.empty:
        return pd.DataFrame()
    cols = ["DriverNumber","BroadcastName","Abbreviation","TeamName","Position","ClassifiedPosition","GridPosition","Time","Status","Points"]
    available = [c for c in cols if c in results.columns]
    return results[available].reset_index(drop=True)

def get_lap_data(year, rnd, stype="R", driver=None):
    session = _load_session(year, rnd, stype)
    laps = session.laps
    if laps is None or laps.empty:
        return pd.DataFrame()
    if driver:
        laps = laps.pick_drivers(driver)
    cols = ["Driver","DriverNumber","LapNumber","LapTime","Sector1Time","Sector2Time","Sector3Time","SpeedI1","SpeedI2","SpeedFL","SpeedST","Compound","TyreLife","FreshTyre","Stint","IsPersonalBest"]
    available = [c for c in cols if c in laps.columns]
    df = laps[available].copy()
    for col in ["LapTime","Sector1Time","Sector2Time","Sector3Time"]:
        if col in df.columns:
            df[col] = df[col].dt.total_seconds()
    return df.reset_index(drop=True)

def get_telemetry(year, rnd, driver, stype="R", lap_number=None):
    session = _load_session(year, rnd, stype)
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
    cols = ["Distance","Speed","Throttle","Brake","nGear","RPM","DRS","X","Y","Z"]
    available = [c for c in cols if c in telemetry.columns]
    return telemetry[available].reset_index(drop=True)

def get_tire_strategy(year, rnd, stype="R"):
    session = _load_session(year, rnd, stype)
    laps = session.laps
    if laps is None or laps.empty:
        return pd.DataFrame()
    stints = (laps.groupby(["Driver","Stint","Compound"]).agg(StintStartLap=("LapNumber","min"),StintEndLap=("LapNumber","max"),TotalLaps=("LapNumber","count")).reset_index())
    return stints.sort_values(["Driver","Stint"]).reset_index(drop=True)

def get_race_results(year, rnd):
    return get_session_results(year, rnd, "R")

def get_driver_season_stats(year, driver):
    schedule = get_event_schedule(year)
    stats = {"driver": driver, "year": year, "races": 0, "wins": 0, "podiums": 0, "poles": 0, "points": 0.0, "avg_finish": 0.0, "avg_grid": 0.0, "dnfs": 0, "fastest_laps": 0}
    finishes, grids = [], []
    for _, event in schedule.iterrows():
        r = int(event["RoundNumber"])
        try:
            results = get_session_results(year, r, "R")
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
    if finishes: stats["avg_finish"] = round(sum(finishes)/len(finishes), 2)
    if grids: stats["avg_grid"] = round(sum(grids)/len(grids), 2)
    return stats

def get_drivers_comparison(year, drivers):
    return [get_driver_season_stats(year, d) for d in drivers]
'''
w('data/fastf1_loader.py', loader)

# models.py
models = '''"""Pydantic models for Pitwall.ai API responses."""
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
    compound: Optional[str] = None
    tyre_life: Optional[int] = None
    stint: Optional[int] = None

class TelemetryPoint(BaseModel):
    distance: float
    speed: float
    throttle: float
    brake: float
    gear: int
    rpm: Optional[int] = None
    drs: Optional[int] = None

class TireStrategy(BaseModel):
    driver: str
    stint: int
    compound: str
    stint_start_lap: int
    stint_end_lap: int
    total_laps: int

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
'''
w('data/models.py', models)

# routers/race.py
race_router = '''"""Race data API routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from data.fastf1_loader import get_event_schedule, get_session_results, get_lap_data, get_telemetry, get_tire_strategy

router = APIRouter(prefix="/api/races", tags=["races"])

@router.get("/{year}")
async def list_races(year: int):
    try:
        schedule = get_event_schedule(year)
        events = []
        for _, row in schedule.iterrows():
            events.append({"round_number": int(row["RoundNumber"]), "country": str(row.get("Country","")), "location": str(row.get("Location","")), "event_name": str(row.get("OfficialEventName", row.get("EventName",""))), "event_date": str(row.get("EventDate","")) if row.get("EventDate") is not None else None, "event_format": str(row.get("EventFormat",""))})
        return {"year": year, "total_races": len(events), "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/{round_number}/results")
async def race_results(year: int, round_number: int, session: str = Query(default="R")):
    try:
        results = get_session_results(year, round_number, session)
        if results.empty:
            return {"year": year, "round": round_number, "session": session, "results": []}
        records = results.to_dict(orient="records")
        for r in records:
            for k, v in r.items():
                if hasattr(v, "total_seconds"): r[k] = v.total_seconds()
        return {"year": year, "round": round_number, "session": session, "results": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/{round_number}/laps")
async def lap_data(year: int, round_number: int, driver: Optional[str] = Query(default=None), session: str = Query(default="R")):
    try:
        laps = get_lap_data(year, round_number, session, driver)
        if laps.empty:
            return {"year": year, "round": round_number, "laps": []}
        return {"year": year, "round": round_number, "driver": driver, "total_laps": len(laps), "laps": laps.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/{round_number}/telemetry/{driver}")
async def driver_telemetry(year: int, round_number: int, driver: str, lap: Optional[int] = Query(default=None), session: str = Query(default="R")):
    try:
        tel = get_telemetry(year, round_number, driver, session, lap)
        if tel.empty:
            return {"year": year, "round": round_number, "driver": driver, "telemetry": []}
        return {"year": year, "round": round_number, "driver": driver, "lap": lap or "fastest", "data_points": len(tel), "telemetry": tel.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/{round_number}/strategy")
async def tire_strategy(year: int, round_number: int, session: str = Query(default="R")):
    try:
        strategy = get_tire_strategy(year, round_number, session)
        if strategy.empty:
            return {"year": year, "round": round_number, "strategy": []}
        return {"year": year, "round": round_number, "total_stints": len(strategy), "strategy": strategy.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
w('routers/race.py', race_router)

# routers/drivers.py
drivers_router = '''"""Driver data API routes."""
from fastapi import APIRouter, HTTPException, Query
from data.fastf1_loader import get_event_schedule, get_session_results, get_driver_season_stats, get_drivers_comparison

router = APIRouter(prefix="/api/drivers", tags=["drivers"])

@router.get("/{year}")
async def list_drivers(year: int):
    try:
        schedule = get_event_schedule(year)
        for _, event in schedule.iterrows():
            rnd = int(event["RoundNumber"])
            try:
                results = get_session_results(year, rnd, "R")
                if not results.empty:
                    drivers = []
                    for _, row in results.iterrows():
                        drivers.append({"driver_number": str(row.get("DriverNumber","")), "broadcast_name": str(row.get("BroadcastName","")), "abbreviation": str(row.get("Abbreviation","")), "team_name": str(row.get("TeamName",""))})
                    return {"year": year, "total_drivers": len(drivers), "drivers": drivers}
            except Exception:
                continue
        return {"year": year, "total_drivers": 0, "drivers": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/{driver_code}/stats")
async def driver_stats(year: int, driver_code: str):
    try:
        return get_driver_season_stats(year, driver_code.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{year}/compare")
async def compare_drivers(year: int, drivers: str = Query(..., description="Comma-separated driver codes")):
    try:
        driver_list = [d.strip().upper() for d in drivers.split(",") if d.strip()]
        if len(driver_list) < 2:
            raise HTTPException(status_code=400, detail="Provide at least 2 driver codes")
        return {"year": year, "drivers": get_drivers_comparison(year, driver_list)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
w('routers/drivers.py', drivers_router)

# main.py
main_py = '''"""Pitwall.ai - F1 Analytics API"""
import os, logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1
from routers.race import router as race_router
from routers.drivers import router as drivers_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

app = FastAPI(title="Pitwall.ai", description="F1 Analytics API", version="0.1.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(race_router)
app.include_router(drivers_router)

@app.get("/")
async def root():
    return {"service": "Pitwall.ai", "version": "0.1.0", "status": "running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
'''
w('main.py', main_py)

# .gitignore
w('.gitignore', '__pycache__/\n*.py[cod]\n*.so\n.env\n.venv\nvenv/\ncache/\n*.log\n*.egg-info/\ndist/\nbuild/\n')

print('\n=== Backend build complete ===')
for root, dirs, files in os.walk(base):
    for f in files:
        p = os.path.join(root, f)
        print(f'  {os.path.relpath(p, base)} ({os.path.getsize(p)} bytes)')
