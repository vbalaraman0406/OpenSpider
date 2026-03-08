import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Created: {path}')

# f1_data.py - FastF1 data service
f1_data_content = '''"""FastF1 data service module for Pitwall.ai."""
import os
import fastf1
import pandas as pd
from typing import Optional

CACHE_DIR = os.environ.get("CACHE_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache"))
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def _load_session(year: int, round_num: int, session_type: str):
    """Load and return a FastF1 session with data."""
    session = fastf1.get_session(year, round_num, session_type)
    session.load()
    return session


def get_race_results(year: int, round_num: int) -> list:
    """Fetch race classification results."""
    session = _load_session(year, round_num, "R")
    results = session.results
    output = []
    for _, row in results.iterrows():
        first = row.get("FirstName", "")
        last = row.get("LastName", "")
        output.append({
            "position": int(row["Position"]) if pd.notna(row["Position"]) else None,
            "driver_number": str(row["DriverNumber"]),
            "driver": row["Abbreviation"],
            "full_name": first + " " + last,
            "team": row["TeamName"],
            "status": row["Status"],
            "points": float(row["Points"]) if pd.notna(row["Points"]) else 0,
            "grid_position": int(row["GridPosition"]) if pd.notna(row["GridPosition"]) else None,
            "time": str(row["Time"]) if pd.notna(row.get("Time")) else None,
        })
    return output


def get_qualifying_results(year: int, round_num: int) -> list:
    """Fetch qualifying session results."""
    session = _load_session(year, round_num, "Q")
    results = session.results
    output = []
    for _, row in results.iterrows():
        first = row.get("FirstName", "")
        last = row.get("LastName", "")
        output.append({
            "position": int(row["Position"]) if pd.notna(row["Position"]) else None,
            "driver": row["Abbreviation"],
            "full_name": first + " " + last,
            "team": row["TeamName"],
            "q1": str(row["Q1"]) if pd.notna(row.get("Q1")) else None,
            "q2": str(row["Q2"]) if pd.notna(row.get("Q2")) else None,
            "q3": str(row["Q3"]) if pd.notna(row.get("Q3")) else None,
        })
    return output


def get_lap_data(year: int, round_num: int) -> list:
    """Fetch lap-by-lap timing data for all drivers."""
    session = _load_session(year, round_num, "R")
    laps = session.laps
    output = []
    for _, lap in laps.iterrows():
        lap_time_sec = lap["LapTime"].total_seconds() if pd.notna(lap["LapTime"]) else None
        output.append({
            "driver": lap["Driver"],
            "lap_number": int(lap["LapNumber"]),
            "lap_time": lap_time_sec,
            "sector1": lap["Sector1Time"].total_seconds() if pd.notna(lap["Sector1Time"]) else None,
            "sector2": lap["Sector2Time"].total_seconds() if pd.notna(lap["Sector2Time"]) else None,
            "sector3": lap["Sector3Time"].total_seconds() if pd.notna(lap["Sector3Time"]) else None,
            "compound": lap["Compound"] if pd.notna(lap["Compound"]) else None,
            "tyre_life": int(lap["TyreLife"]) if pd.notna(lap["TyreLife"]) else None,
            "position": int(lap["Position"]) if pd.notna(lap["Position"]) else None,
        })
    return output


def get_driver_telemetry(year: int, round_num: int, driver_code: str) -> dict:
    """Fetch telemetry data for a specific driver\'s fastest lap."""
    session = _load_session(year, round_num, "R")
    laps = session.laps
    driver_laps = laps.pick_driver(driver_code)
    fastest = driver_laps.pick_fastest()
    telemetry = fastest.get_telemetry()
    tel_data = []
    # Sample every 5th point to reduce payload size
    for i, (_, t) in enumerate(telemetry.iterrows()):
        if i % 5 != 0:
            continue
        tel_data.append({
            "distance": float(t["Distance"]) if pd.notna(t["Distance"]) else None,
            "speed": float(t["Speed"]) if pd.notna(t["Speed"]) else None,
            "throttle": float(t["Throttle"]) if pd.notna(t["Throttle"]) else None,
            "brake": bool(t["Brake"]) if pd.notna(t["Brake"]) else None,
            "gear": int(t["nGear"]) if pd.notna(t["nGear"]) else None,
            "rpm": int(t["RPM"]) if pd.notna(t["RPM"]) else None,
            "drs": int(t["DRS"]) if pd.notna(t["DRS"]) else None,
        })
    return {
        "driver": driver_code,
        "lap_time": str(fastest["LapTime"]),
        "lap_number": int(fastest["LapNumber"]),
        "compound": fastest["Compound"],
        "telemetry": tel_data,
    }


def get_tire_strategy(year: int, round_num: int) -> list:
    """Fetch tire strategy data for all drivers."""
    session = _load_session(year, round_num, "R")
    laps = session.laps
    strategies = []
    for driver in session.drivers:
        d_laps = laps.pick_driver(driver)
        if d_laps.empty:
            continue
        info = session.get_driver(driver)
        first = info.get("FirstName", "")
        last = info.get("LastName", "")
        stints = []
        for stint_num, stint_laps in d_laps.groupby("Stint"):
            first_lap = stint_laps.iloc[0]
            stints.append({
                "stint": int(stint_num),
                "compound": first_lap["Compound"] if pd.notna(first_lap["Compound"]) else "UNKNOWN",
                "laps": len(stint_laps),
                "start_lap": int(stint_laps["LapNumber"].min()),
                "end_lap": int(stint_laps["LapNumber"].max()),
            })
        strategies.append({
            "driver": info["Abbreviation"],
            "full_name": first + " " + last,
            "team": info["TeamName"],
            "stints": stints,
        })
    return strategies
'''

write('backend/app/f1_data.py', f1_data_content)

# main.py - FastAPI application
main_content = '''"""Pitwall.ai - FastAPI Backend Application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(
    title="Pitwall.ai API",
    description="F1 Analytics Dashboard Backend",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2025 Season Calendar
SEASON_2025 = [
    {"round": 1, "name": "Australian Grand Prix", "circuit": "Albert Park", "country": "Australia", "date": "2025-03-16"},
    {"round": 2, "name": "Chinese Grand Prix", "circuit": "Shanghai International", "country": "China", "date": "2025-03-23"},
    {"round": 3, "name": "Japanese Grand Prix", "circuit": "Suzuka", "country": "Japan", "date": "2025-04-06"},
    {"round": 4, "name": "Bahrain Grand Prix", "circuit": "Sakhir", "country": "Bahrain", "date": "2025-04-13"},
    {"round": 5, "name": "Saudi Arabian Grand Prix", "circuit": "Jeddah Corniche", "country": "Saudi Arabia", "date": "2025-04-20"},
    {"round": 6, "name": "Miami Grand Prix", "circuit": "Miami International", "country": "USA", "date": "2025-05-04"},
    {"round": 7, "name": "Emilia Romagna Grand Prix", "circuit": "Imola", "country": "Italy", "date": "2025-05-18"},
    {"round": 8, "name": "Monaco Grand Prix", "circuit": "Monte Carlo", "country": "Monaco", "date": "2025-05-25"},
    {"round": 9, "name": "Spanish Grand Prix", "circuit": "Barcelona-Catalunya", "country": "Spain", "date": "2025-06-01"},
    {"round": 10, "name": "Canadian Grand Prix", "circuit": "Gilles Villeneuve", "country": "Canada", "date": "2025-06-15"},
    {"round": 11, "name": "Austrian Grand Prix", "circuit": "Red Bull Ring", "country": "Austria", "date": "2025-06-29"},
    {"round": 12, "name": "British Grand Prix", "circuit": "Silverstone", "country": "UK", "date": "2025-07-06"},
    {"round": 13, "name": "Belgian Grand Prix", "circuit": "Spa-Francorchamps", "country": "Belgium", "date": "2025-07-27"},
    {"round": 14, "name": "Hungarian Grand Prix", "circuit": "Hungaroring", "country": "Hungary", "date": "2025-08-03"},
    {"round": 15, "name": "Dutch Grand Prix", "circuit": "Zandvoort", "country": "Netherlands", "date": "2025-08-31"},
    {"round": 16, "name": "Italian Grand Prix", "circuit": "Monza", "country": "Italy", "date": "2025-09-07"},
    {"round": 17, "name": "Azerbaijan Grand Prix", "circuit": "Baku City", "country": "Azerbaijan", "date": "2025-09-21"},
    {"round": 18, "name": "Singapore Grand Prix", "circuit": "Marina Bay", "country": "Singapore", "date": "2025-10-05"},
    {"round": 19, "name": "United States Grand Prix", "circuit": "COTA", "country": "USA", "date": "2025-10-19"},
    {"round": 20, "name": "Mexico City Grand Prix", "circuit": "Hermanos Rodriguez", "country": "Mexico", "date": "2025-10-26"},
    {"round": 21, "name": "Brazilian Grand Prix", "circuit": "Interlagos", "country": "Brazil", "date": "2025-11-09"},
    {"round": 22, "name": "Las Vegas Grand Prix", "circuit": "Las Vegas Strip", "country": "USA", "date": "2025-11-22"},
    {"round": 23, "name": "Qatar Grand Prix", "circuit": "Lusail", "country": "Qatar", "date": "2025-11-30"},
    {"round": 24, "name": "Abu Dhabi Grand Prix", "circuit": "Yas Marina", "country": "UAE", "date": "2025-12-07"},
]

# 2025 Driver lineup
DRIVERS_2025 = [
    {"code": "VER", "name": "Max Verstappen", "number": 1, "team": "Red Bull Racing", "country": "NED"},
    {"code": "LAW", "name": "Liam Lawson", "number": 30, "team": "Red Bull Racing", "country": "NZL"},
    {"code": "NOR", "name": "Lando Norris", "number": 4, "team": "McLaren", "country": "GBR"},
    {"code": "PIA", "name": "Oscar Piastri", "number": 81, "team": "McLaren", "country": "AUS"},
    {"code": "HAM", "name": "Lewis Hamilton", "number": 44, "team": "Ferrari", "country": "GBR"},
    {"code": "LEC", "name": "Charles Leclerc", "number": 16, "team": "Ferrari", "country": "MON"},
    {"code": "RUS", "name": "George Russell", "number": 63, "team": "Mercedes", "country": "GBR"},
    {"code": "ANT", "name": "Andrea Kimi Antonelli", "number": 12, "team": "Mercedes", "country": "ITA"},
    {"code": "ALO", "name": "Fernando Alonso", "number": 14, "team": "Aston Martin", "country": "ESP"},
    {"code": "STR", "name": "Lance Stroll", "number": 18, "team": "Aston Martin", "country": "CAN"},
    {"code": "GAS", "name": "Pierre Gasly", "number": 10, "team": "Alpine", "country": "FRA"},
    {"code": "DOO", "name": "Jack Doohan", "number": 7, "team": "Alpine", "country": "AUS"},
    {"code": "ALB", "name": "Alexander Albon", "number": 23, "team": "Williams", "country": "THA"},
    {"code": "SAI", "name": "Carlos Sainz Jr.", "number": 55, "team": "Williams", "country": "ESP"},
    {"code": "TSU", "name": "Yuki Tsunoda", "number": 22, "team": "RB", "country": "JPN"},
    {"code": "HAD", "name": "Isack Hadjar", "number": 6, "team": "RB", "country": "FRA"},
    {"code": "HUL", "name": "Nico Hulkenberg", "number": 27, "team": "Sauber", "country": "GER"},
    {"code": "BOR", "name": "Gabriel Bortoleto", "number": 5, "team": "Sauber", "country": "BRA"},
    {"code": "BEA", "name": "Oliver Bearman", "number": 87, "team": "Haas", "country": "GBR"},
    {"code": "OCO", "name": "Esteban Ocon", "number": 31, "team": "Haas", "country": "FRA"},
]


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "online", "service": "pitwall.ai", "version": "1.0.0"}


@app.get("/api/races")
async def list_races(year: int = 2025):
    """List available races for a season."""
    return {"year": year, "races": SEASON_2025}


@app.get("/api/drivers")
async def list_drivers():
    """List all 2025 drivers."""
    return {"season": 2025, "drivers": DRIVERS_2025}


@app.get("/api/race/{year}/{round_num}/results")
async def race_results(year: int, round_num: int):
    """Fetch race results using FastF1."""
    try:
        from app.f1_data import get_race_results
        results = get_race_results(year, round_num)
        return {"year": year, "round": round_num, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/race/{year}/{round_num}/qualifying")
async def qualifying_results(year: int, round_num: int):
    """Fetch qualifying results using FastF1."""
    try:
        from app.f1_data import get_qualifying_results
        results = get_qualifying_results(year, round_num)
        return {"year": year, "round": round_num, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/race/{year}/{round_num}/laps")
async def lap_data(year: int, round_num: int):
    """Fetch lap time data using FastF1."""
    try:
        from app.f1_data import get_lap_data
        laps = get_lap_data(year, round_num)
        return {"year": year, "round": round_num, "total_laps": len(laps), "laps": laps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/race/{year}/{round_num}/telemetry/{driver}")
async def driver_telemetry(year: int, round_num: int, driver: str):
    """Fetch driver telemetry for fastest lap."""
    try:
        from app.f1_data import get_driver_telemetry
        data = get_driver_telemetry(year, round_num, driver.upper())
        return {"year": year, "round": round_num, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/race/{year}/{round_num}/strategy")
async def tire_strategy(year: int, round_num: int):
    """Fetch tire strategy data."""
    try:
        from app.f1_data import get_tire_strategy
        strategies = get_tire_strategy(year, round_num)
        return {"year": year, "round": round_num, "strategies": strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

write('backend/app/main.py', main_content)

print('Batch 2 complete: f1_data.py, main.py')
