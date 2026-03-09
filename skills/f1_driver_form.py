"""
f1_driver_form.py — Driver/team form analysis.
Fetches current season results, calculates momentum, head-to-head vs teammate.
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
    driver = (args.get("driver", "") or "").strip().lower()
    team = (args.get("team", "") or "").strip().lower()
    compare = args.get("compare", [])
    year = args.get("year", "current")

    # Driver form mode
    if driver:
        # Get results
        results_data = fetch_json(f"{JOLPICA_BASE}/{year}/drivers/{driver}/results.json?limit=30")
        quali_data = fetch_json(f"{JOLPICA_BASE}/{year}/drivers/{driver}/qualifying.json?limit=30")

        if "error" in results_data:
            return results_data

        races = results_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        quali_races = quali_data.get("MRData", {}).get("RaceTable", {}).get("Races", []) if "error" not in quali_data else []

        if not races:
            return {"error": f"No results found for driver '{driver}' in {year}"}

        race_results = []
        total_points = 0
        total_pos = 0
        dnfs = 0
        podiums = 0
        wins = 0
        team_name = ""

        for r in races:
            for res in r.get("Results", []):
                pos = res.get("position", "0")
                pts = float(res.get("points", 0))
                status = res.get("status", "")
                team_name = res.get("Constructor", {}).get("name", "")

                is_dnf = pos == "R" or "Retired" in status or "Accident" in status or "Collision" in status
                pos_int = int(pos) if pos.isdigit() else 20

                race_results.append({
                    "round": r["round"],
                    "race": r["raceName"],
                    "position": pos_int if not is_dnf else "DNF",
                    "grid": int(res.get("grid", 0)),
                    "points": pts,
                    "status": status,
                })

                total_points += pts
                if not is_dnf:
                    total_pos += pos_int
                else:
                    dnfs += 1
                if pos_int <= 3 and not is_dnf:
                    podiums += 1
                if pos_int == 1 and not is_dnf:
                    wins += 1

        finished_races = len(race_results) - dnfs
        avg_finish = round(total_pos / finished_races, 2) if finished_races > 0 else 0

        # Momentum: compare last 3 vs first 3 average position
        if len(race_results) >= 6:
            first3 = [r["position"] for r in race_results[:3] if r["position"] != "DNF"]
            last3 = [r["position"] for r in race_results[-3:] if r["position"] != "DNF"]
            first_avg = sum(first3) / len(first3) if first3 else 10
            last_avg = sum(last3) / len(last3) if last3 else 10
            momentum = "📈 Improving" if last_avg < first_avg else ("📉 Declining" if last_avg > first_avg else "➡️ Stable")
        else:
            momentum = "➡️ Insufficient data"

        return {
            "driver": driver,
            "team": team_name,
            "season": str(year),
            "race_results": race_results[-10:],
            "stats": {
                "total_points": total_points,
                "races": len(race_results),
                "wins": wins,
                "podiums": podiums,
                "dnfs": dnfs,
                "average_finish": avg_finish,
                "dnf_rate_pct": round((dnfs / len(race_results)) * 100, 1) if race_results else 0,
                "momentum": momentum,
            },
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    # Team form mode
    if team:
        data = fetch_json(f"{JOLPICA_BASE}/{year}/constructors/{team}/results.json?limit=60")
        if "error" in data:
            return data

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return {"error": f"No results for team '{team}' in {year}"}

        driver_stats = {}
        total_pts = 0

        for r in races:
            for res in r.get("Results", []):
                did = res["Driver"]["driverId"]
                dname = f"{res['Driver']['givenName']} {res['Driver']['familyName']}"
                pts = float(res.get("points", 0))
                pos = int(res.get("position", 20)) if res.get("position", "0").isdigit() else 20
                total_pts += pts

                if did not in driver_stats:
                    driver_stats[did] = {"name": dname, "points": 0, "races": 0, "avg_pos": 0, "total_pos": 0}
                driver_stats[did]["points"] += pts
                driver_stats[did]["races"] += 1
                driver_stats[did]["total_pos"] += pos

        for did in driver_stats:
            ds = driver_stats[did]
            ds["avg_pos"] = round(ds["total_pos"] / ds["races"], 2) if ds["races"] > 0 else 0

        return {
            "team": team,
            "season": str(year),
            "total_points": total_pts,
            "drivers": driver_stats,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    # Compare mode
    if compare and isinstance(compare, list) and len(compare) >= 2:
        comparisons = []
        for d in compare[:4]:
            result = execute({"driver": d.strip().lower(), "year": year})
            if "error" not in result:
                comparisons.append(result)
        return {"comparison": comparisons, "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

    return {"error": "Provide 'driver', 'team', or 'compare'. Examples: {\"driver\": \"hamilton\"}, {\"team\": \"ferrari\"}, {\"compare\": [\"hamilton\", \"russell\"]}"}
