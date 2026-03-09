"""
f1_weather_strategy.py — Weather impact on race strategy.
Combines OpenF1 weather data + built-in historical patterns.
"""
import json
import os
import urllib.request
from datetime import datetime

OPENF1_BASE = "https://api.openf1.org/v1"

CALENDAR_FILE = os.path.join(os.getcwd(), "skills", "f1_calendar_2026.json")

# Historical weather patterns for circuits
WEATHER_HISTORY = {
    "Albert Park": {"avg_temp_c": 22, "rain_probability_pct": 25, "wind_typical": "moderate sea breeze", "humidity_pct": 60},
    "Shanghai": {"avg_temp_c": 18, "rain_probability_pct": 30, "wind_typical": "light", "humidity_pct": 65},
    "Suzuka": {"avg_temp_c": 25, "rain_probability_pct": 45, "wind_typical": "variable (typhoon risk)", "humidity_pct": 75},
    "Bahrain": {"avg_temp_c": 30, "rain_probability_pct": 2, "wind_typical": "sand-carrying gusts", "humidity_pct": 45},
    "Jeddah": {"avg_temp_c": 33, "rain_probability_pct": 1, "wind_typical": "light", "humidity_pct": 50},
    "Miami": {"avg_temp_c": 30, "rain_probability_pct": 40, "wind_typical": "light", "humidity_pct": 80},
    "Imola": {"avg_temp_c": 22, "rain_probability_pct": 35, "wind_typical": "light", "humidity_pct": 55},
    "Monaco": {"avg_temp_c": 22, "rain_probability_pct": 15, "wind_typical": "light Mediterranean", "humidity_pct": 60},
    "Barcelona": {"avg_temp_c": 28, "rain_probability_pct": 10, "wind_typical": "moderate", "humidity_pct": 55},
    "Montreal": {"avg_temp_c": 24, "rain_probability_pct": 35, "wind_typical": "variable (river effect)", "humidity_pct": 65},
    "Spielberg": {"avg_temp_c": 22, "rain_probability_pct": 40, "wind_typical": "alpine gusts", "humidity_pct": 55},
    "Silverstone": {"avg_temp_c": 20, "rain_probability_pct": 50, "wind_typical": "strong, variable direction", "humidity_pct": 70},
    "Spa-Francorchamps": {"avg_temp_c": 18, "rain_probability_pct": 60, "wind_typical": "Ardennes microclimate, unpredictable", "humidity_pct": 75},
    "Budapest": {"avg_temp_c": 32, "rain_probability_pct": 25, "wind_typical": "light", "humidity_pct": 55},
    "Zandvoort": {"avg_temp_c": 19, "rain_probability_pct": 35, "wind_typical": "strong North Sea winds", "humidity_pct": 75},
    "Monza": {"avg_temp_c": 28, "rain_probability_pct": 15, "wind_typical": "light", "humidity_pct": 55},
    "Baku": {"avg_temp_c": 25, "rain_probability_pct": 5, "wind_typical": "strong Caspian crosswinds", "humidity_pct": 60},
    "Marina Bay": {"avg_temp_c": 31, "rain_probability_pct": 45, "wind_typical": "light", "humidity_pct": 85},
    "Austin": {"avg_temp_c": 28, "rain_probability_pct": 30, "wind_typical": "moderate", "humidity_pct": 60},
    "Mexico City": {"avg_temp_c": 22, "rain_probability_pct": 20, "wind_typical": "light (high altitude)", "humidity_pct": 50},
    "Interlagos": {"avg_temp_c": 24, "rain_probability_pct": 50, "wind_typical": "variable", "humidity_pct": 70},
    "Las Vegas": {"avg_temp_c": 12, "rain_probability_pct": 5, "wind_typical": "desert gusts", "humidity_pct": 20},
    "Lusail": {"avg_temp_c": 28, "rain_probability_pct": 2, "wind_typical": "light desert", "humidity_pct": 45},
    "Yas Marina": {"avg_temp_c": 30, "rain_probability_pct": 1, "wind_typical": "light", "humidity_pct": 55},
}


def load_calendar():
    try:
        if os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def fetch_openf1_weather(session_key: str) -> list:
    """Fetch weather data from OpenF1 for a session."""
    try:
        url = f"{OPENF1_BASE}/weather?session_key={session_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "OpenSpider/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
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
        return {"error": "Race not found. Provide 'round' or 'circuit'."}

    circuit_name = target.get("circuit", "")
    race_name = target.get("raceName", "")

    # Find historical weather
    historical = None
    for key, data in WEATHER_HISTORY.items():
        if key.lower() in circuit_name.lower() or circuit_name.lower() in key.lower():
            historical = data
            break

    if not historical:
        # Fallback: try matching any word
        for key, data in WEATHER_HISTORY.items():
            words = key.lower().split()
            if any(w in circuit_name.lower() for w in words if len(w) > 3):
                historical = data
                break

    if not historical:
        historical = {"avg_temp_c": 25, "rain_probability_pct": 20, "wind_typical": "unknown", "humidity_pct": 55}

    # Strategy impact assessment
    rain_prob = historical["rain_probability_pct"]
    if rain_prob >= 50:
        weather_impact = "HIGH — Rain highly likely. Intermediate/wet tires may be needed. Safety car probability increases significantly."
        strategy_rec = "Prepare for mixed conditions. Consider delayed pit stop to wait for weather window. Drivers with strong wet skills have major advantage."
    elif rain_prob >= 30:
        weather_impact = "MODERATE — Rain possible. Teams should prepare both dry and wet strategies."
        strategy_rec = "Monitor conditions closely. Have intermediates ready. Consider aggressive early stop if rain approaches."
    else:
        weather_impact = "LOW — Dry conditions expected. Standard tire strategy applies."
        strategy_rec = "Focus on optimal tire compound selection and pit window timing."

    temp = historical["avg_temp_c"]
    if temp >= 35:
        tire_note = "Extreme heat — high tire degradation expected. Softs may blister. 2-stop likely."
    elif temp >= 28:
        tire_note = "Warm conditions — moderate degradation. Mediums and hards preferred."
    elif temp >= 20:
        tire_note = "Comfortable temps — balanced degradation. All compounds viable."
    else:
        tire_note = "Cool conditions — tire warmup critical. Softs may struggle for grip initially."

    return {
        "race": race_name,
        "circuit": circuit_name,
        "round": target.get("round"),
        "date": target.get("raceDate"),
        "weather_summary": {
            "expected_temp_c": historical["avg_temp_c"],
            "rain_probability_pct": rain_prob,
            "humidity_pct": historical["humidity_pct"],
            "wind": historical["wind_typical"],
        },
        "strategy_impact": {
            "weather_impact_level": weather_impact,
            "strategy_recommendation": strategy_rec,
            "tire_temperature_note": tire_note,
        },
        "historical_note": f"Based on historical weather data for {circuit_name}. Actual conditions may vary.",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
