import os

base = 'workspace/pitwall-ai/backend'

os.makedirs(f'{base}/routers', exist_ok=True)
os.makedirs(f'{base}/data', exist_ok=True)

files = {}

files[f'{base}/routers/__init__.py'] = '# Pitwall.ai routers\n'

files[f'{base}/data/__init__.py'] = '# Pitwall.ai data module\n'

files[f'{base}/routers/race.py'] = '''from fastapi import APIRouter, Query
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/races", tags=["races"])

SAMPLE_RACES = [
    {"round": 1, "name": "Australian Grand Prix", "circuit": "Albert Park", "date": "2026-03-08", "country": "AUS", "winner": "George Russell", "completed": True},
    {"round": 2, "name": "Chinese Grand Prix", "circuit": "Shanghai International", "date": "2026-03-15", "country": "CHN", "completed": False},
    {"round": 3, "name": "Japanese Grand Prix", "circuit": "Suzuka", "date": "2026-03-29", "country": "JPN", "completed": False},
    {"round": 4, "name": "Bahrain Grand Prix", "circuit": "Sakhir", "date": "2026-04-12", "country": "BHR", "completed": False},
    {"round": 5, "name": "Saudi Arabian Grand Prix", "circuit": "Jeddah", "date": "2026-04-19", "country": "KSA", "completed": False},
    {"round": 6, "name": "Miami Grand Prix", "circuit": "Miami International", "date": "2026-05-03", "country": "USA", "completed": False},
]

SAMPLE_RESULTS = [
    {"position": 1, "driver": "George Russell", "team": "Mercedes", "time": "1:32:46.123", "points": 25},
    {"position": 2, "driver": "Kimi Antonelli", "team": "Mercedes", "time": "+2.974s", "points": 18},
    {"position": 3, "driver": "Charles Leclerc", "team": "Ferrari", "time": "+15.519s", "points": 15},
    {"position": 4, "driver": "Lewis Hamilton", "team": "Ferrari", "time": "+22.341s", "points": 12},
    {"position": 5, "driver": "Lando Norris", "team": "McLaren", "time": "+28.876s", "points": 10},
    {"position": 6, "driver": "Max Verstappen", "team": "Red Bull", "time": "+35.221s", "points": 8},
    {"position": 7, "driver": "Oliver Bearman", "team": "Haas", "time": "+45.109s", "points": 6},
    {"position": 8, "driver": "Arvid Lindblad", "team": "Racing Bulls", "time": "+50.332s", "points": 4},
    {"position": 9, "driver": "Gabriel Bortoleto", "team": "Sauber", "time": "+55.887s", "points": 2},
    {"position": 10, "driver": "Pierre Gasly", "team": "Alpine", "time": "+60.112s", "points": 1},
]


@router.get("/{year}")
async def list_races(year: int):
    """List all races for a season."""
    try:
        import fastf1
        schedule = fastf1.get_event_schedule(year)
        races = []
        for _, event in schedule.iterrows():
            if event["EventFormat"] == "testing":
                continue
            races.append({
                "round": int(event["RoundNumber"]),
                "name": event["EventName"],
                "circuit": event.get("Location", "TBD"),
                "date": str(event["EventDate"].date()) if hasattr(event["EventDate"], "date") else str(event["EventDate"]),
                "country": event.get("Country", "TBD"),
                "completed": False,
                "winner": None,
            })
        return races
    except Exception as e:
        logger.warning(f"FastF1 schedule fetch failed: {e}. Using sample data.")
        return SAMPLE_RACES


@router.get("/{year}/{round}/results")
async def race_results(year: int, round: int, session: Optional[str] = Query("R", description="Session: R=Race, Q=Qualifying, FP1/FP2/FP3")):
    """Get race or session results."""
    try:
        import fastf1
        sess = fastf1.get_session(year, round, session)
        sess.load()
        results = []
        for _, row in sess.results.iterrows():
            results.append({
                "position": int(row["Position"]) if not str(row["Position"]).startswith("R") else None,
                "driver": row["FullName"],
                "team": row["TeamName"],
                "time": str(row.get("Time", "")),
                "points": float(row.get("Points", 0)),
            })
        return results
    except Exception as e:
        logger.warning(f"FastF1 results fetch failed: {e}. Using sample data.")
        return SAMPLE_RESULTS


@router.get("/{year}/{round}/laps")
async def race_laps(year: int, round: int, driver: Optional[str] = None):
    """Get lap-by-lap timing data."""
    try:
        import fastf1
        sess = fastf1.get_session(year, round, "R")
        sess.load()
        laps = sess.laps
        if driver:
            laps = laps.pick_driver(driver)
        result = []
        for _, lap in laps.iterrows():
            result.append({
                "driver": lap["Driver"],
                "lap": int(lap["LapNumber"]),
                "time": str(lap["LapTime"]) if lap["LapTime"] is not None else None,
                "sector1": str(lap.get("Sector1Time", "")) if lap.get("Sector1Time") is not None else None,
                "sector2": str(lap.get("Sector2Time", "")) if lap.get("Sector2Time") is not None else None,
                "sector3": str(lap.get("Sector3Time", "")) if lap.get("Sector3Time") is not None else None,
                "compound": lap.get("Compound", "UNKNOWN"),
            })
        return result
    except Exception as e:
        logger.warning(f"FastF1 laps fetch failed: {e}")
        return []


@router.get("/{year}/{round}/telemetry/{driver}")
async def driver_telemetry(year: int, round: int, driver: str):
    """Get car telemetry for a specific driver."""
    try:
        import fastf1
        sess = fastf1.get_session(year, round, "R")
        sess.load()
        drv_laps = sess.laps.pick_driver(driver)
        fastest = drv_laps.pick_fastest()
        tel = fastest.get_car_data().add_distance()
        result = []
        for _, row in tel.iterrows():
            result.append({
                "distance": float(row["Distance"]),
                "speed": float(row["Speed"]),
                "throttle": float(row["Throttle"]),
                "brake": bool(row["Brake"]),
                "gear": int(row["nGear"]),
                "drs": int(row.get("DRS", 0)),
            })
        return result
    except Exception as e:
        logger.warning(f"FastF1 telemetry fetch failed: {e}")
        return []


@router.get("/{year}/{round}/strategy")
async def race_strategy(year: int, round: int):
    """Get tire strategy data for all drivers."""
    try:
        import fastf1
        sess = fastf1.get_session(year, round, "R")
        sess.load()
        stints = []
        for drv in sess.laps["Driver"].unique():
            drv_laps = sess.laps.pick_driver(drv)
            for stint_num in drv_laps["Stint"].unique():
                stint_laps = drv_laps[drv_laps["Stint"] == stint_num]
                stints.append({
                    "driver": drv,
                    "stint": int(stint_num),
                    "compound": stint_laps["Compound"].iloc[0] if len(stint_laps) > 0 else "UNKNOWN",
                    "laps": len(stint_laps),
                    "start_lap": int(stint_laps["LapNumber"].min()),
                })
        return stints
    except Exception as e:
        logger.warning(f"FastF1 strategy fetch failed: {e}")
        return []
'''

files[f'{base}/routers/drivers.py'] = '''from fastapi import APIRouter, Query
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/drivers", tags=["drivers"])

SAMPLE_DRIVERS = [
    {"code": "RUS", "name": "George Russell", "team": "Mercedes", "number": 63, "points": 25, "wins": 1, "podiums": 1},
    {"code": "ANT", "name": "Kimi Antonelli", "team": "Mercedes", "number": 12, "points": 18, "wins": 0, "podiums": 1},
    {"code": "LEC", "name": "Charles Leclerc", "team": "Ferrari", "number": 16, "points": 15, "wins": 0, "podiums": 1},
    {"code": "HAM", "name": "Lewis Hamilton", "team": "Ferrari", "number": 44, "points": 12, "wins": 0, "podiums": 0},
    {"code": "NOR", "name": "Lando Norris", "team": "McLaren", "number": 4, "points": 10, "wins": 0, "podiums": 0},
    {"code": "VER", "name": "Max Verstappen", "team": "Red Bull", "number": 1, "points": 8, "wins": 0, "podiums": 0},
    {"code": "BEA", "name": "Oliver Bearman", "team": "Haas", "number": 87, "points": 6, "wins": 0, "podiums": 0},
    {"code": "LIN", "name": "Arvid Lindblad", "team": "Racing Bulls", "number": 40, "points": 4, "wins": 0, "podiums": 0},
    {"code": "BOR", "name": "Gabriel Bortoleto", "team": "Sauber", "number": 5, "points": 2, "wins": 0, "podiums": 0},
    {"code": "GAS", "name": "Pierre Gasly", "team": "Alpine", "number": 10, "points": 1, "wins": 0, "podiums": 0},
]


@router.get("/{year}")
async def list_drivers(year: int):
    """List all drivers for a season."""
    try:
        import fastf1
        schedule = fastf1.get_event_schedule(year)
        last_round = None
        for _, event in schedule.iterrows():
            if event["EventFormat"] != "testing":
                last_round = int(event["RoundNumber"])
        if last_round:
            sess = fastf1.get_session(year, 1, "R")
            sess.load()
            drivers = []
            for _, row in sess.results.iterrows():
                drivers.append({
                    "code": row["Abbreviation"],
                    "name": row["FullName"],
                    "team": row["TeamName"],
                    "number": int(row["DriverNumber"]),
                    "points": float(row.get("Points", 0)),
                    "wins": 0,
                    "podiums": 0,
                })
            return sorted(drivers, key=lambda x: x["points"], reverse=True)
    except Exception as e:
        logger.warning(f"FastF1 drivers fetch failed: {e}. Using sample data.")
    return SAMPLE_DRIVERS


@router.get("/{year}/{code}/stats")
async def driver_stats(year: int, code: str):
    """Get aggregated stats for a driver."""
    for d in SAMPLE_DRIVERS:
        if d["code"] == code.upper():
            return {
                **d,
                "avg_finish": 1.0 if d["wins"] > 0 else 5.0,
                "avg_quali": 2.0,
                "fastest_laps": 0,
                "dnfs": 0,
                "races": 1,
            }
    return {"error": "Driver not found"}


@router.get("/{year}/compare")
async def compare_drivers(year: int, drivers: str = Query(..., description="Comma-separated driver codes")):
    """Compare two or more drivers head-to-head."""
    codes = [c.strip().upper() for c in drivers.split(",")]
    results = []
    for code in codes:
        for d in SAMPLE_DRIVERS:
            if d["code"] == code:
                results.append({
                    "driver": code,
                    "points": d["points"],
                    "wins": d["wins"],
                    "podiums": d["podiums"],
                    "avg_finish": 1.0 if d["wins"] > 0 else 5.0,
                    "avg_quali": 2.0,
                    "dnfs": 0,
                })
                break
    return results
'''

files[f'{base}/data/fastf1_loader.py'] = '''"""FastF1 data loading utilities for Pitwall.ai"""
import fastf1
import pandas as pd
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def load_session(year: int, round_num: int, session_type: str = "R"):
    """Load a FastF1 session with caching."""
    try:
        session = fastf1.get_session(year, round_num, session_type)
        session.load()
        return session
    except Exception as e:
        logger.error(f"Failed to load session {year} R{round_num} {session_type}: {e}")
        return None


def get_lap_data(session, driver: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extract lap timing data from a session."""
    if session is None:
        return []
    laps = session.laps
    if driver:
        laps = laps.pick_driver(driver)
    result = []
    for _, lap in laps.iterrows():
        result.append({
            "driver": lap["Driver"],
            "lap": int(lap["LapNumber"]),
            "time": str(lap["LapTime"]) if pd.notna(lap["LapTime"]) else None,
            "sector1": str(lap["Sector1Time"]) if pd.notna(lap.get("Sector1Time")) else None,
            "sector2": str(lap["Sector2Time"]) if pd.notna(lap.get("Sector2Time")) else None,
            "sector3": str(lap["Sector3Time"]) if pd.notna(lap.get("Sector3Time")) else None,
            "compound": lap.get("Compound", "UNKNOWN"),
            "tyre_life": int(lap.get("TyreLife", 0)) if pd.notna(lap.get("TyreLife")) else 0,
        })
    return result


def get_telemetry(session, driver: str, lap: str = "fastest") -> List[Dict[str, Any]]:
    """Extract car telemetry for a driver."""
    if session is None:
        return []
    try:
        drv_laps = session.laps.pick_driver(driver)
        if lap == "fastest":
            target_lap = drv_laps.pick_fastest()
        else:
            target_lap = drv_laps[drv_laps["LapNumber"] == int(lap)].iloc[0]
        tel = target_lap.get_car_data().add_distance()
        result = []
        for _, row in tel.iterrows():
            result.append({
                "distance": float(row["Distance"]),
                "speed": float(row["Speed"]),
                "throttle": float(row["Throttle"]),
                "brake": bool(row["Brake"]),
                "gear": int(row["nGear"]),
                "drs": int(row.get("DRS", 0)),
            })
        return result
    except Exception as e:
        logger.error(f"Telemetry extraction failed for {driver}: {e}")
        return []


def get_tire_strategy(session) -> List[Dict[str, Any]]:
    """Extract tire strategy stints for all drivers."""
    if session is None:
        return []
    stints = []
    for drv in session.laps["Driver"].unique():
        drv_laps = session.laps.pick_driver(drv)
        for stint_num in drv_laps["Stint"].unique():
            stint_laps = drv_laps[drv_laps["Stint"] == stint_num]
            stints.append({
                "driver": drv,
                "stint": int(stint_num),
                "compound": stint_laps["Compound"].iloc[0] if len(stint_laps) > 0 else "UNKNOWN",
                "laps": len(stint_laps),
                "start_lap": int(stint_laps["LapNumber"].min()),
            })
    return stints
'''

files[f'{base}/data/models.py'] = '''"""Pydantic models for Pitwall.ai API responses."""
from pydantic import BaseModel
from typing import Optional, List


class RaceInfo(BaseModel):
    round: int
    name: str
    circuit: str
    date: str
    country: str
    winner: Optional[str] = None
    completed: bool = False


class RaceResult(BaseModel):
    position: Optional[int]
    driver: str
    team: str
    time: str
    points: float


class LapData(BaseModel):
    driver: str
    lap: int
    time: Optional[str]
    sector1: Optional[str]
    sector2: Optional[str]
    sector3: Optional[str]
    compound: str


class TelemetryPoint(BaseModel):
    distance: float
    speed: float
    throttle: float
    brake: bool
    gear: int
    drs: int


class TireStint(BaseModel):
    driver: str
    stint: int
    compound: str
    laps: int
    start_lap: int


class DriverInfo(BaseModel):
    code: str
    name: str
    team: str
    number: int
    points: float
    wins: int
    podiums: int


class DriverStats(BaseModel):
    code: str
    name: str
    team: str
    number: int
    points: float
    wins: int
    podiums: int
    avg_finish: float
    avg_quali: float
    fastest_laps: int
    dnfs: int
    races: int


class CompareResult(BaseModel):
    driver: str
    points: float
    wins: int
    podiums: int
    avg_finish: float
    avg_quali: float
    dnfs: int
'''

for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content)
    print(f'  OK {path}')

print(f'\nBackend build complete. {len(files)} files written.')
