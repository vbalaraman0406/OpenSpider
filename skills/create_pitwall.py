import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Created: {path}')

# 1. README.md
write('README.md', '''# Pitwall.ai - F1 Analytics Dashboard

> Real-time Formula 1 race analytics, telemetry visualization, and predictive insights.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, FastAPI, FastF1, Pandas, scikit-learn |
| **Frontend** | React 18, Tailwind CSS, Recharts |
| **Hosting** | Google App Engine |
| **Data** | FastF1 (Official F1 Timing Data) |

## Features

- Race results and classification tables
- Lap time analysis with interactive charts
- Driver telemetry comparison (speed, throttle, brake, gear)
- Tire strategy visualization
- Head-to-head driver statistics
- Predictive race modeling (coming soon)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Roadmap

- [x] Project scaffolding
- [x] FastF1 data integration
- [x] Race dashboard with results table
- [x] Lap time charts
- [ ] Live timing integration
- [ ] ML-based race predictions
- [ ] Weather impact analysis
- [ ] Custom domain setup

## License

MIT
''')

# 2. .gitignore
write('.gitignore', '''# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.env
venv/
*.egg
.f1cache/
cache/

# Node
node_modules/
.next/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
*.log
''')

# 3. backend/requirements.txt
write('backend/requirements.txt', '''fastf1==3.7.0
fastapi==0.115.0
uvicorn[standard]==0.30.0
pandas==2.2.0
numpy==1.26.0
scikit-learn==1.4.0
python-dotenv==1.0.0
gunicorn==22.0.0
''')

# 4. backend/app/__init__.py
write('backend/app/__init__.py', '')

# 5. backend/app/f1_data.py
write('backend/app/f1_data.py', '''"""FastF1 data service module for Pitwall.ai."""
import os
import fastf1
import pandas as pd
from typing import Optional

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def _load_session(year: int, round_num: int, session_type: str):
    """Load and return a FastF1 session with data."""
    session = fastf1.get_session(year, round_num, session_type)
    session.load()
    return session


def get_race_results(year: int, round_num: int) -> list[dict]:
    """Fetch race classification results."""
    session = _load_session(year, round_num, "R")
    results = session.results
    output = []
    for _, row in results.iterrows():
        output.append({
            "position": int(row["Position"]) if pd.notna(row["Position"]) else None,
            "driver_number": str(row["DriverNumber"]),
            "driver": row["Abbreviation"],
            "full_name": f"{row["FirstName"]} {row["LastName"]}",
            "team": row["TeamName"],
            "status": row["Status"],
            "points": float(row["Points"]) if pd.notna(row["Points"]) else 0,
            "grid_position": int(row["GridPosition"]) if pd.notna(row["GridPosition"]) else None,
            "time": str(row["Time"]) if pd.notna(row.get("Time")) else None,
        })
    return output


def get_qualifying_results(year: int, round_num: int) -> list[dict]:
    """Fetch qualifying session results."""
    session = _load_session(year, round_num, "Q")
    results = session.results
    output = []
    for _, row in results.iterrows():
        output.append({
            "position": int(row["Position"]) if pd.notna(row["Position"]) else None,
            "driver": row["Abbreviation"],
            "full_name": f"{row["FirstName"]} {row["LastName"]}",
            "team": row["TeamName"],
            "q1": str(row["Q1"]) if pd.notna(row.get("Q1")) else None,
            "q2": str(row["Q2"]) if pd.notna(row.get("Q2")) else None,
            "q3": str(row["Q3"]) if pd.notna(row.get("Q3")) else None,
        })
    return output


def get_lap_data(year: int, round_num: int) -> list[dict]:
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
            "speed_trap": float(lap["SpeedST"]) if pd.notna(lap.get("SpeedST")) else None,
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
    for _, t in telemetry.iterrows():
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


def get_tire_strategy(year: int, round_num: int) -> list[dict]:
    """Fetch tire strategy data for all drivers."""
    session = _load_session(year, round_num, "R")
    laps = session.laps
    strategies = []
    for driver in session.drivers:
        d_laps = laps.pick_driver(driver)
        if d_laps.empty:
            continue
        info = session.get_driver(driver)
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
            "full_name": f"{info["FirstName"]} {info["LastName"]}",
            "team": info["TeamName"],
            "stints": stints,
        })
    return strategies
''')

print('First batch done. Continuing...')
