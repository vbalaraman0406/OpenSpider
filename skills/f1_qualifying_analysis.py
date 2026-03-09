"""
f1_qualifying_analysis.py — Qualifying performance breakdown.
Fetches Q1/Q2/Q3 times, gaps to pole, head-to-head vs teammate.
Uses Jolpica (Ergast-compatible) API.
"""
import json
import urllib.request
from datetime import datetime

JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"


def fetch_json(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenSpider/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def execute(args: dict) -> dict:
    year = args.get("year", "current")
    round_num = args.get("round")
    driver = (args.get("driver", "") or "").strip().lower()

    # Mode 1: Specific race qualifying results
    if round_num:
        url = f"{JOLPICA_BASE}/{year}/{round_num}/qualifying.json"
        data = fetch_json(url)
        if "error" in data:
            return data

        try:
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if not races:
                return {"error": f"No qualifying data for {year} round {round_num}"}

            race = races[0]
            results = []
            for q in race.get("QualifyingResults", []):
                results.append({
                    "position": int(q.get("position", 0)),
                    "driver": f"{q['Driver']['givenName']} {q['Driver']['familyName']}",
                    "driver_id": q["Driver"]["driverId"],
                    "team": q["Constructor"]["name"],
                    "Q1": q.get("Q1", "—"),
                    "Q2": q.get("Q2", "—"),
                    "Q3": q.get("Q3", "—"),
                })

            # Calculate gaps to pole
            pole_time = results[0].get("Q3", "") if results else ""
            if pole_time and pole_time != "—":
                pole_secs = time_to_seconds(pole_time)
                for r in results:
                    best = r.get("Q3") or r.get("Q2") or r.get("Q1") or ""
                    if best and best != "—":
                        gap = time_to_seconds(best) - pole_secs
                        r["gap_to_pole"] = f"+{gap:.3f}s" if gap > 0 else "POLE"

            return {
                "race": race.get("raceName", ""),
                "circuit": race.get("Circuit", {}).get("circuitName", ""),
                "season": race.get("season", year),
                "round": round_num,
                "qualifying_results": results,
                "pole_sitter": results[0] if results else None,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        except Exception as e:
            return {"error": str(e)}

    # Mode 2: Driver qualifying history
    if driver:
        url = f"{JOLPICA_BASE}/{year}/drivers/{driver}/qualifying.json?limit=30"
        data = fetch_json(url)
        if "error" in data:
            return data

        try:
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            entries = []
            total_pos = 0
            poles = 0
            front_rows = 0

            for race in races:
                for q in race.get("QualifyingResults", []):
                    pos = int(q.get("position", 0))
                    entry = {
                        "round": race["round"],
                        "race": race["raceName"],
                        "position": pos,
                        "Q1": q.get("Q1", "—"),
                        "Q2": q.get("Q2", "—"),
                        "Q3": q.get("Q3", "—"),
                    }
                    entries.append(entry)
                    total_pos += pos
                    if pos == 1:
                        poles += 1
                    if pos <= 3:
                        front_rows += 1

            avg_pos = round(total_pos / len(entries), 2) if entries else 0

            return {
                "driver": driver,
                "season": str(year),
                "qualifying_entries": entries[-10:],
                "stats": {
                    "average_qualifying_position": avg_pos,
                    "poles": poles,
                    "front_row_starts": front_rows,
                    "total_qualifyings": len(entries),
                },
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Provide 'round' (with optional 'year') or 'driver'. Examples: {\"round\": 5} or {\"driver\": \"verstappen\"}"}


def time_to_seconds(time_str: str) -> float:
    """Convert lap time string (M:SS.mmm) to seconds."""
    try:
        parts = time_str.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0
