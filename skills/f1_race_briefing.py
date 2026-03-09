"""
f1_race_briefing.py — Complete race weekend preview.
Combines data from all other F1 skills into one comprehensive briefing.
"""
import json
import os
import sys
from datetime import datetime

CALENDAR_FILE = os.path.join(os.getcwd(), "skills", "f1_calendar_2026.json")
SKILLS_DIR = os.path.join(os.getcwd(), "skills")


def load_calendar():
    try:
        if os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def run_skill(skill_name: str, args: dict) -> dict:
    """Execute another skill and return its result."""
    try:
        skill_path = os.path.join(SKILLS_DIR, f"{skill_name}.py")
        if not os.path.exists(skill_path):
            return {"error": f"Skill {skill_name} not found"}

        # Import and execute the skill
        import importlib.util
        spec = importlib.util.spec_from_file_location(skill_name, skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.execute(args)
    except Exception as e:
        return {"error": f"Skill {skill_name} failed: {str(e)}"}


def execute(args: dict) -> dict:
    round_arg = args.get("round", "next")
    calendar = load_calendar()

    # Resolve target race
    target = None
    if str(round_arg).lower() == "next":
        today = datetime.utcnow().strftime("%Y-%m-%d")
        for r in calendar:
            if r.get("raceDate", "") >= today:
                target = r
                break
    else:
        try:
            round_num = int(round_arg)
            target = next((r for r in calendar if r["round"] == round_num), None)
        except (ValueError, TypeError):
            # Try name match
            query = str(round_arg).lower()
            target = next((r for r in calendar if query in r.get("raceName", "").lower()
                           or query in r.get("circuit", "").lower()), None)

    if not target:
        return {"error": "Race not found. Provide 'round' number or 'next'.",
                "schedule": [f"R{r['round']}: {r['raceName']} ({r['raceDate']})" for r in calendar]}

    round_num = target["round"]
    race_name = target.get("raceName", "")
    circuit = target.get("circuit", "")
    race_date = target.get("raceDate", "")

    briefing = {
        "title": f"🏁 Race Briefing: {race_name}",
        "round": round_num,
        "circuit": circuit,
        "date": race_date,
    }

    # 1. Track Intelligence
    track_data = run_skill("f1_track_intelligence", {"circuit": circuit})
    if "error" not in track_data:
        briefing["track_profile"] = {
            "length_km": track_data.get("length_km"),
            "laps": track_data.get("laps"),
            "turns": track_data.get("turns"),
            "drs_zones": track_data.get("drs_zones"),
            "lap_record": track_data.get("lap_record"),
            "overtaking_rating": f"{track_data.get('overtaking_rating', '?')}/10",
            "key_corners": track_data.get("key_corners", []),
            "favors": track_data.get("favors"),
        }

    # 2. Weather
    weather_data = run_skill("f1_weather_strategy", {"round": round_num})
    if "error" not in weather_data:
        briefing["weather"] = weather_data.get("weather_summary", {})
        briefing["weather_strategy_impact"] = weather_data.get("strategy_impact", {})

    # 3. Tire Strategy
    tire_data = run_skill("f1_tire_strategy", {"round": round_num})
    if "error" not in tire_data:
        briefing["tire_strategy"] = {
            "optimal": tire_data.get("optimal_strategy"),
            "compound_life": tire_data.get("compound_life"),
            "pit_window": tire_data.get("pit_window"),
            "degradation": tire_data.get("degradation"),
            "safety_car_probability_pct": tire_data.get("safety_car_probability_pct"),
        }

    # 4. Predictions
    prediction_data = run_skill("f1_race_predictor", {"round": round_num})
    if "error" not in prediction_data:
        briefing["predictions"] = {
            "predicted_pole": prediction_data.get("predicted_pole", [])[:3],
            "predicted_winner": prediction_data.get("predicted_winner", [])[:3],
            "confidence_pct": prediction_data.get("confidence_pct"),
        }

    # 5. Schedule
    briefing["schedule"] = {
        "note": "Exact session times vary by circuit timezone. Check formula1.com for local times.",
        "friday": "Practice 1, Practice 2",
        "saturday": "Practice 3, Qualifying",
        "sunday": f"Race — {target.get('raceDate', '')}",
    }

    briefing["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    briefing["disclaimer"] = "Predictions are probabilistic estimates. F1 is inherently unpredictable."

    return briefing
