#!/usr/bin/env python3
"""Ingest 2025 (or 2024 fallback) Australian GP data via FastF1."""

import json
import os
import sys
from pathlib import Path
from datetime import timedelta

import fastf1
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
CACHE_DIR = BASE_DIR / "cache"
DATA_DIR = BASE_DIR / "data"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def td_to_str(td):
    """Convert timedelta / NaT to a readable string."""
    if pd.isna(td):
        return None
    if isinstance(td, timedelta):
        total = td.total_seconds()
        mins = int(total // 60)
        secs = total - mins * 60
        if mins > 0:
            return f"{mins}:{secs:06.3f}"
        return f"{secs:.3f}"
    return str(td)


def safe_float(v):
    if pd.isna(v):
        return None
    return float(v)


def safe_int(v):
    if pd.isna(v):
        return None
    return int(v)


# ---------------------------------------------------------------------------
# Load session – try 2025 first, fall back to 2024
# ---------------------------------------------------------------------------
year = 2025
try:
    print(f"[*] Attempting to load {year} Australian GP Race...")
    race = fastf1.get_session(year, 'Australia', 'R')
    race.load()
    print(f"[+] Successfully loaded {year} Australian GP Race.")
except Exception as e:
    print(f"[!] {year} failed ({e}). Falling back to 2024...")
    year = 2024
    race = fastf1.get_session(year, 'Australia', 'R')
    race.load()
    print(f"[+] Successfully loaded {year} Australian GP Race.")

# ---------------------------------------------------------------------------
# 1. Race Results
# ---------------------------------------------------------------------------
print("[*] Extracting race results...")
results = race.results
race_results = []
for _, r in results.iterrows():
    race_results.append({
        "position": safe_int(r.get("Position")),
        "classified_position": str(r.get("ClassifiedPosition", "")),
        "driver": r.get("Abbreviation", ""),
        "driver_number": str(r.get("DriverNumber", "")),
        "full_name": r.get("FullName", ""),
        "team": r.get("TeamName", ""),
        "team_color": r.get("TeamColor", ""),
        "grid_position": safe_int(r.get("GridPosition")),
        "time": td_to_str(r.get("Time")),
        "status": r.get("Status", ""),
        "points": safe_float(r.get("Points")),
    })

with open(DATA_DIR / "race_results.json", "w") as f:
    json.dump({"year": year, "gp": "Australia", "session": "Race", "results": race_results}, f, indent=2)
print(f"    -> Saved {len(race_results)} drivers to race_results.json")

# ---------------------------------------------------------------------------
# 2. Lap Times
# ---------------------------------------------------------------------------
print("[*] Extracting lap times...")
laps = race.laps
lap_records = []
for _, lp in laps.iterrows():
    lap_records.append({
        "driver": lp.get("Driver", ""),
        "driver_number": str(lp.get("DriverNumber", "")),
        "lap_number": safe_int(lp.get("LapNumber")),
        "lap_time": td_to_str(lp.get("LapTime")),
        "sector1": td_to_str(lp.get("Sector1Time")),
        "sector2": td_to_str(lp.get("Sector2Time")),
        "sector3": td_to_str(lp.get("Sector3Time")),
        "compound": lp.get("Compound", None),
        "tyre_life": safe_float(lp.get("TyreLife")),
        "fresh_tyre": bool(lp.get("FreshTyre")) if not pd.isna(lp.get("FreshTyre")) else None,
        "stint": safe_int(lp.get("Stint")),
        "position": safe_float(lp.get("Position")),
        "is_accurate": bool(lp.get("IsAccurate")) if not pd.isna(lp.get("IsAccurate")) else None,
    })

with open(DATA_DIR / "lap_times.json", "w") as f:
    json.dump({"year": year, "gp": "Australia", "session": "Race", "total_laps_recorded": len(lap_records), "laps": lap_records}, f, indent=2)
print(f"    -> Saved {len(lap_records)} lap records to lap_times.json")

# ---------------------------------------------------------------------------
# 3. Qualifying Results
# ---------------------------------------------------------------------------
print("[*] Extracting qualifying results...")
try:
    quali = fastf1.get_session(year, 'Australia', 'Q')
    quali.load()
    qr = quali.results
    quali_results = []
    for _, r in qr.iterrows():
        quali_results.append({
            "position": safe_int(r.get("Position")),
            "driver": r.get("Abbreviation", ""),
            "full_name": r.get("FullName", ""),
            "team": r.get("TeamName", ""),
            "q1": td_to_str(r.get("Q1")),
            "q2": td_to_str(r.get("Q2")),
            "q3": td_to_str(r.get("Q3")),
        })
    with open(DATA_DIR / "qualifying_results.json", "w") as f:
        json.dump({"year": year, "gp": "Australia", "session": "Qualifying", "results": quali_results}, f, indent=2)
    print(f"    -> Saved {len(quali_results)} drivers to qualifying_results.json")
except Exception as e:
    print(f"    [!] Qualifying load failed: {e}")
    with open(DATA_DIR / "qualifying_results.json", "w") as f:
        json.dump({"year": year, "gp": "Australia", "session": "Qualifying", "error": str(e)}, f, indent=2)

# ---------------------------------------------------------------------------
# 4. Race Summary
# ---------------------------------------------------------------------------
print("[*] Building race summary...")

# Winner
winner = race_results[0] if race_results else {}

# Fastest lap
fastest = laps.pick_fastest()
fastest_lap_info = {
    "driver": fastest["Driver"] if fastest is not None else None,
    "lap_number": safe_int(fastest["LapNumber"]) if fastest is not None else None,
    "lap_time": td_to_str(fastest["LapTime"]) if fastest is not None else None,
}

# Weather
weather_summary = None
try:
    wd = race.weather_data
    if wd is not None and len(wd) > 0:
        weather_summary = {
            "air_temp_avg": round(wd["AirTemp"].mean(), 1),
            "track_temp_avg": round(wd["TrackTemp"].mean(), 1),
            "humidity_avg": round(wd["Humidity"].mean(), 1),
            "rainfall": bool(wd["Rainfall"].any()),
            "wind_speed_avg": round(wd["WindSpeed"].mean(), 1),
        }
except Exception:
    pass

# Total laps
total_laps = int(laps["LapNumber"].max()) if len(laps) > 0 else None

summary = {
    "year": year,
    "gp": "Australia",
    "circuit": race.event["EventName"] if hasattr(race, 'event') else "Albert Park",
    "winner": winner,
    "fastest_lap": fastest_lap_info,
    "total_laps": total_laps,
    "total_drivers": len(race_results),
    "weather": weather_summary,
}

with open(DATA_DIR / "race_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"    -> Saved race_summary.json")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"  INGESTION COMPLETE — {year} Australian GP")
print("=" * 60)
print(f"  Winner:       {winner.get('full_name', 'N/A')} ({winner.get('team', 'N/A')})")
print(f"  Fastest Lap:  {fastest_lap_info['driver']} — {fastest_lap_info['lap_time']} (Lap {fastest_lap_info['lap_number']})")
print(f"  Total Laps:   {total_laps}")
print(f"  Drivers:      {len(race_results)}")
print(f"  Lap Records:  {len(lap_records)}")
if weather_summary:
    print(f"  Weather:      Air {weather_summary['air_temp_avg']}°C | Track {weather_summary['track_temp_avg']}°C | Rain: {weather_summary['rainfall']}")
print(f"\n  Files saved to: {DATA_DIR}/")
for fn in ["race_results.json", "lap_times.json", "qualifying_results.json", "race_summary.json"]:
    fp = DATA_DIR / fn
    size = fp.stat().st_size if fp.exists() else 0
    print(f"    {fn}: {size:,} bytes")
print("=" * 60)
