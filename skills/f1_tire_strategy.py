"""
f1_tire_strategy.py — Pit stop and tire compound analysis.
Built-in database of tire strategies per circuit with compound life estimates.
"""
import json
import os
from datetime import datetime

CALENDAR_FILE = os.path.join(os.getcwd(), "skills", "f1_calendar_2026.json")

# Tire strategy database per circuit
TIRE_STRATEGIES = {
    "Albert Park": {
        "laps": 58, "pit_loss_sec": 22,
        "optimal_strategy": "1 stop (M→H) or 2 stop (S→M→H)",
        "compound_life": {"soft": "15-18 laps", "medium": "25-30 laps", "hard": "35-40 laps"},
        "pit_window": "Lap 18-24 (1-stop) or Laps 15, 35 (2-stop)",
        "degradation": "Medium — rear-limited, traction zones",
        "undercut_power": "Strong (3-5 tenths per lap)",
        "overcut_power": "Moderate",
        "safety_car_probability_pct": 45,
        "notes": "Track evolution significant. Later stints faster as rubber is laid down."
    },
    "Bahrain": {
        "laps": 57, "pit_loss_sec": 22,
        "optimal_strategy": "2 stop (S→H→M) or 1 stop (M→H)",
        "compound_life": {"soft": "12-15 laps", "medium": "22-26 laps", "hard": "32-38 laps"},
        "pit_window": "Laps 14, 36 (2-stop) or Lap 20-24 (1-stop)",
        "degradation": "High — abrasive surface, rear-limited",
        "undercut_power": "Very strong (can gain 1+ seconds)",
        "overcut_power": "Weak",
        "safety_car_probability_pct": 30,
        "notes": "Tire degradation is the defining factor. Night race means consistent track temps."
    },
    "Monaco": {
        "laps": 78, "pit_loss_sec": 20,
        "optimal_strategy": "1 stop (M→H) — overcut preferred",
        "compound_life": {"soft": "30-35 laps", "medium": "40-50 laps", "hard": "55-65 laps"},
        "pit_window": "Lap 30-40 (wait for safety car if possible)",
        "degradation": "Very low — smooth surface, low-speed",
        "undercut_power": "Low (no overtaking to capitalize)",
        "overcut_power": "KING — track position is everything",
        "safety_car_probability_pct": 60,
        "notes": "Strategy almost irrelevant — track position wins. Pray for safety car to free-stop."
    },
    "Silverstone": {
        "laps": 52, "pit_loss_sec": 22,
        "optimal_strategy": "1 stop (M→H) or 2 stop (S→M→S)",
        "compound_life": {"soft": "14-18 laps", "medium": "22-28 laps", "hard": "30-38 laps"},
        "pit_window": "Lap 18-22 (1-stop) or Laps 14, 32 (2-stop)",
        "degradation": "Medium-High — high-speed corners stress front-left",
        "undercut_power": "Strong",
        "overcut_power": "Moderate (new tires are significant)",
        "safety_car_probability_pct": 35,
        "notes": "Front-left tire is critical at Copse and Maggotts-Becketts. Weather can change everything."
    },
    "Spa-Francorchamps": {
        "laps": 44, "pit_loss_sec": 24,
        "optimal_strategy": "1 stop (M→H)",
        "compound_life": {"soft": "15-18 laps", "medium": "22-28 laps", "hard": "30-36 laps"},
        "pit_window": "Lap 18-24",
        "degradation": "Medium — balanced, long lap reduces stint counts",
        "undercut_power": "Strong (long pit straight helps)",
        "overcut_power": "Moderate",
        "safety_car_probability_pct": 40,
        "notes": "Rain can force switch to intermediates at any moment. Eau Rouge incidents common."
    },
    "Monza": {
        "laps": 53, "pit_loss_sec": 23,
        "optimal_strategy": "1 stop (M→H)",
        "compound_life": {"soft": "18-22 laps", "medium": "28-32 laps", "hard": "38-44 laps"},
        "pit_window": "Lap 22-28",
        "degradation": "Low — mostly straight-line, low lateral G",
        "undercut_power": "Moderate",
        "overcut_power": "Moderate",
        "safety_car_probability_pct": 25,
        "notes": "Tires last long at Monza. Power/drag matters more than tire strategy."
    },
    "Marina Bay": {
        "laps": 62, "pit_loss_sec": 28,
        "optimal_strategy": "2 stop (S→M→S) or 1 stop (M→H)",
        "compound_life": {"soft": "14-18 laps", "medium": "24-28 laps", "hard": "34-40 laps"},
        "pit_window": "Laps 16, 38 (2-stop) or Lap 22-26 (1-stop)",
        "degradation": "High — bumpy surface, heat, humidity",
        "undercut_power": "Strong",
        "overcut_power": "Moderate",
        "safety_car_probability_pct": 65,
        "notes": "Very physical race for drivers. High safety car probability often reshuffles strategy."
    },
    "Baku": {
        "laps": 51, "pit_loss_sec": 25,
        "optimal_strategy": "1 stop (H→M) — front-load hard tire",
        "compound_life": {"soft": "12-16 laps", "medium": "22-26 laps", "hard": "30-36 laps"},
        "pit_window": "Lap 25-32 (react to safety car)",
        "degradation": "Medium — rear degradation from traction zones",
        "undercut_power": "Moderate (long pit lane)",
        "overcut_power": "Strong (safety car pit opportunity)",
        "safety_car_probability_pct": 70,
        "notes": "BAKU IS CHAOS. Safety cars are almost guaranteed. Strategy flexibility is key."
    },
}


def load_calendar():
    try:
        if os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def execute(args: dict) -> dict:
    round_num = args.get("round")
    circuit_query = (args.get("circuit", "") or "").strip().lower()

    calendar = load_calendar()
    target = None

    if round_num:
        target = next((r for r in calendar if r["round"] == int(round_num)), None)
    elif circuit_query:
        target = next((r for r in calendar if circuit_query in r.get("circuit", "").lower()
                       or circuit_query in r.get("raceName", "").lower()), None)
    else:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        for r in calendar:
            if r.get("raceDate", "") >= today:
                target = r
                break

    if not target:
        return {"error": "Race not found. Provide 'round' or 'circuit'.",
                "available": sorted(TIRE_STRATEGIES.keys())}

    circuit_name = target.get("circuit", "")

    # Find strategy data
    strategy = None
    for key, data in TIRE_STRATEGIES.items():
        if key.lower() in circuit_name.lower() or circuit_name.lower() in key.lower():
            strategy = data
            break

    if not strategy:
        for key, data in TIRE_STRATEGIES.items():
            words = key.lower().split()
            if any(w in circuit_name.lower() for w in words if len(w) > 3):
                strategy = data
                break

    if not strategy:
        return {
            "race": target.get("raceName", ""),
            "circuit": circuit_name,
            "message": "Detailed tire strategy data not yet available for this circuit.",
            "general_advice": "Typically a 1-2 stop race. Medium → Hard is the safe baseline. Monitor real-time degradation.",
            "available_circuits": sorted(TIRE_STRATEGIES.keys()),
        }

    result = dict(strategy)
    result["race"] = target.get("raceName", "")
    result["circuit"] = circuit_name
    result["round"] = target.get("round")
    result["date"] = target.get("raceDate")
    result["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return result
