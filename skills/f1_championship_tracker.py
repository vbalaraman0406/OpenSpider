"""
f1_championship_tracker.py — Live standings + title math.
Uses Jolpica API for current driver and constructor standings.
"""
import json
import urllib.request
from datetime import datetime

JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"

MAX_POINTS_PER_RACE = 26  # Win(25) + Fastest Lap(1)
MAX_POINTS_PER_SPRINT = 8  # Sprint win
TOTAL_ROUNDS_2026 = 24
SPRINT_ROUNDS_2026 = 6


def fetch_json(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenSpider/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def execute(args: dict) -> dict:
    standings_type = (args.get("type", "drivers") or "drivers").lower()
    year = args.get("year", "current")

    if standings_type in ("drivers", "driver", "wdc"):
        data = fetch_json(f"{JOLPICA_BASE}/{year}/driverStandings.json")
        if "error" in data:
            return data

        try:
            standings_list = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if not standings_list:
                return {"error": f"No driver standings for {year}"}

            sl = standings_list[0]
            season = sl.get("season", str(year))
            round_num = int(sl.get("round", 0))
            remaining = TOTAL_ROUNDS_2026 - round_num

            drivers = []
            leader_points = 0

            for ds in sl.get("DriverStandings", []):
                pos = int(ds.get("position", 0))
                points = float(ds.get("points", 0))
                wins = int(ds.get("wins", 0))
                driver = ds.get("Driver", {})
                constructor = ds.get("Constructors", [{}])[0] if ds.get("Constructors") else {}

                if pos == 1:
                    leader_points = points

                max_remaining = remaining * MAX_POINTS_PER_RACE + min(remaining, SPRINT_ROUNDS_2026) * MAX_POINTS_PER_SPRINT
                max_possible = points + max_remaining
                gap = points - leader_points

                can_win = max_possible >= leader_points

                drivers.append({
                    "position": pos,
                    "driver": f"{driver.get('givenName', '')} {driver.get('familyName', '')}",
                    "driver_id": driver.get("driverId", ""),
                    "nationality": driver.get("nationality", ""),
                    "team": constructor.get("name", ""),
                    "points": points,
                    "wins": wins,
                    "gap_to_leader": gap if pos > 1 else 0,
                    "max_possible_points": max_possible,
                    "can_still_win_title": can_win,
                })

            # Key battles
            battles = []
            for i in range(len(drivers) - 1):
                gap = abs(drivers[i]["points"] - drivers[i + 1]["points"])
                if gap <= 30:
                    battles.append(f"{drivers[i]['driver']} vs {drivers[i+1]['driver']} ({gap} pts)")

            return {
                "type": "Driver Championship",
                "season": season,
                "rounds_completed": round_num,
                "rounds_remaining": remaining,
                "standings": drivers[:20],
                "title_contenders": [d for d in drivers if d["can_still_win_title"]],
                "close_battles": battles[:5],
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        except Exception as e:
            return {"error": str(e)}

    elif standings_type in ("constructors", "constructor", "teams", "wcc"):
        data = fetch_json(f"{JOLPICA_BASE}/{year}/constructorStandings.json")
        if "error" in data:
            return data

        try:
            standings_list = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            if not standings_list:
                return {"error": f"No constructor standings for {year}"}

            sl = standings_list[0]
            teams = []
            leader_pts = 0

            for cs in sl.get("ConstructorStandings", []):
                pos = int(cs.get("position", 0))
                pts = float(cs.get("points", 0))
                wins = int(cs.get("wins", 0))
                constructor = cs.get("Constructor", {})

                if pos == 1:
                    leader_pts = pts

                teams.append({
                    "position": pos,
                    "team": constructor.get("name", ""),
                    "nationality": constructor.get("nationality", ""),
                    "points": pts,
                    "wins": wins,
                    "gap_to_leader": pts - leader_pts if pos > 1 else 0,
                })

            return {
                "type": "Constructor Championship",
                "season": sl.get("season", str(year)),
                "rounds_completed": int(sl.get("round", 0)),
                "standings": teams,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Provide 'type' as 'drivers' or 'constructors'. Example: {\"type\": \"drivers\"}"}
