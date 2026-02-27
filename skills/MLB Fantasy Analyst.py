import json
import random
from datetime import datetime, timedelta

# =============================================================================
# MLB Fantasy Baseball Prediction Skill
# =============================================================================
# Evaluates MLB player performance using Statcast metrics, Sabermetrics, and
# 2026 league trends to provide fantasy draft rankings, sleeper picks, and
# daily lineup optimizations.
# =============================================================================

# --- Simulated Player Database (2026 Season) ---
# In a production environment, this would be fetched from Statcast/FanGraphs APIs.

PLAYER_DATABASE = {
    # Hitters
    "shohei ohtani": {
        "name": "Shohei Ohtani",
        "team": "LAD",
        "position": "DH/SP",
        "type": "hitter",
        "xwOBA": 0.410,
        "wOBA": 0.425,
        "barrel_rate": 16.5,
        "sweet_spot_pct": 38.2,
        "avg": 0.285,
        "hr": 22,
        "rbi": 58,
        "sb": 14,
        "ops": 0.975,
        "war": 4.2,
        "adp": 1,
        "park_factor": 97,
        "injury_history": "UCL surgery (2024), returned fully healthy for 2025-2026. No current concerns.",
        "three_year_xwOBA": 0.405,
        "three_year_wOBA": 0.400,
        "games_played_2026": 72,
        "league_pct_barrel": 99,
        "notes": "Elite two-way player. Pitching workload may be managed in 2026."
    },
    "aaron judge": {
        "name": "Aaron Judge",
        "team": "NYY",
        "position": "OF",
        "type": "hitter",
        "xwOBA": 0.415,
        "wOBA": 0.408,
        "barrel_rate": 18.1,
        "sweet_spot_pct": 36.8,
        "avg": 0.278,
        "hr": 26,
        "rbi": 62,
        "sb": 3,
        "ops": 0.990,
        "war": 4.5,
        "adp": 3,
        "park_factor": 101,
        "injury_history": "Toe injury history (2023). Some durability concerns given frame size.",
        "three_year_xwOBA": 0.410,
        "three_year_wOBA": 0.405,
        "games_played_2026": 68,
        "league_pct_barrel": 99,
        "notes": "Buy signal: xwOBA exceeds wOBA, regression upward likely."
    },
    "ronald acuna jr": {
        "name": "Ronald Acuña Jr.",
        "team": "ATL",
        "position": "OF",
        "type": "hitter",
        "xwOBA": 0.370,
        "wOBA": 0.345,
        "barrel_rate": 10.2,
        "sweet_spot_pct": 33.5,
        "avg": 0.258,
        "hr": 10,
        "rbi": 32,
        "sb": 18,
        "ops": 0.810,
        "war": 2.1,
        "adp": 8,
        "park_factor": 100,
        "injury_history": "ACL tear (2024). Returned mid-2025. Knee recovery ongoing - monitoring lateral movement and sprint speed.",
        "three_year_xwOBA": 0.395,
        "three_year_wOBA": 0.390,
        "games_played_2026": 55,
        "league_pct_barrel": 72,
        "notes": "Talent undeniable but health is the #1 risk factor. Speed may not fully return."
    },
    "hunter goodman": {
        "name": "Hunter Goodman",
        "team": "COL",
        "position": "C",
        "type": "hitter",
        "xwOBA": 0.365,
        "wOBA": 0.358,
        "barrel_rate": 14.2,
        "sweet_spot_pct": 37.0,
        "avg": 0.270,
        "hr": 16,
        "rbi": 45,
        "sb": 2,
        "ops": 0.865,
        "war": 2.0,
        "adp": 145,
        "park_factor": 114,
        "injury_history": "No significant injury history.",
        "three_year_xwOBA": 0.340,
        "three_year_wOBA": 0.335,
        "games_played_2026": 65,
        "league_pct_barrel": 95,
        "notes": "Breakout candidate at catcher. Coors Field significantly boosts value."
    },
    "bobby witt jr": {
        "name": "Bobby Witt Jr.",
        "team": "KC",
        "position": "SS",
        "type": "hitter",
        "xwOBA": 0.385,
        "wOBA": 0.392,
        "barrel_rate": 11.8,
        "sweet_spot_pct": 35.5,
        "avg": 0.298,
        "hr": 15,
        "rbi": 48,
        "sb": 22,
        "ops": 0.895,
        "war": 3.8,
        "adp": 5,
        "park_factor": 103,
        "injury_history": "Clean bill of health. Iron man candidate.",
        "three_year_xwOBA": 0.375,
        "three_year_wOBA": 0.380,
        "games_played_2026": 74,
        "league_pct_barrel": 82,
        "notes": "Kauffman Stadium 2026 fence pull-in benefits his power profile. 5-category contributor."
    },
    "mike trout": {
        "name": "Mike Trout",
        "team": "LAA",
        "position": "OF",
        "type": "hitter",
        "xwOBA": 0.380,
        "wOBA": 0.370,
        "barrel_rate": 15.0,
        "sweet_spot_pct": 36.0,
        "avg": 0.265,
        "hr": 12,
        "rbi": 30,
        "sb": 1,
        "ops": 0.870,
        "war": 1.8,
        "adp": 85,
        "park_factor": 96,
        "injury_history": "Chronic knee/calf issues (2021-2025). Meniscus surgery 2024. Limited to <100 games each of last 4 seasons. HIGH DURABILITY RISK.",
        "three_year_xwOBA": 0.385,
        "three_year_wOBA": 0.375,
        "games_played_2026": 42,
        "league_pct_barrel": 96,
        "notes": "When healthy, still elite. The problem is staying healthy. Draft with caution."
    },
    "elly de la cruz": {
        "name": "Elly De La Cruz",
        "team": "CIN",
        "position": "SS",
        "type": "hitter",
        "xwOBA": 0.340,
        "wOBA": 0.355,
        "barrel_rate": 9.5,
        "sweet_spot_pct": 30.2,
        "avg": 0.248,
        "hr": 14,
        "rbi": 38,
        "sb": 35,
        "ops": 0.800,
        "war": 2.8,
        "adp": 12,
        "park_factor": 105,
        "injury_history": "No significant injuries. Young and durable.",
        "three_year_xwOBA": 0.335,
        "three_year_wOBA": 0.340,
        "games_played_2026": 70,
        "league_pct_barrel": 60,
        "notes": "wOBA > xwOBA suggests some overperformance. Elite speed carries massive SB value."
    },
    # Pitchers
    "spencer strider": {
        "name": "Spencer Strider",
        "team": "ATL",
        "position": "SP",
        "type": "pitcher",
        "stuff_plus": 135,
        "location_plus": 108,
        "siera": 2.85,
        "era": 2.95,
        "k_bb_pct": 28.5,
        "k_per_9": 12.8,
        "whip": 0.98,
        "war": 3.5,
        "adp": 15,
        "injury_history": "UCL surgery (2024). Returned mid-2025. Workload managed carefully in 2026.",
        "three_year_siera": 2.90,
        "games_played_2026": 14,
        "innings_2026": 88.0,
        "notes": "Elite stuff. Health is only question. When right, top-5 SP in fantasy."
    },
    "tarik skubal": {
        "name": "Tarik Skubal",
        "team": "DET",
        "position": "SP",
        "type": "pitcher",
        "stuff_plus": 120,
        "location_plus": 118,
        "siera": 2.72,
        "era": 2.55,
        "k_bb_pct": 26.8,
        "k_per_9": 11.2,
        "whip": 0.92,
        "war": 4.0,
        "adp": 10,
        "injury_history": "Flexor strain history (2022-2023). Fully healthy since mid-2024.",
        "three_year_siera": 2.80,
        "games_played_2026": 16,
        "innings_2026": 105.0,
        "notes": "Cy Young caliber. Elite command pairs with good stuff. Premium SP1."
    },
    "paul skenes": {
        "name": "Paul Skenes",
        "team": "PIT",
        "position": "SP",
        "type": "pitcher",
        "stuff_plus": 140,
        "location_plus": 105,
        "siera": 2.95,
        "era": 3.10,
        "k_bb_pct": 25.2,
        "k_per_9": 12.5,
        "whip": 1.05,
        "war": 3.0,
        "adp": 18,
        "injury_history": "No significant injuries. Workload carefully managed as young arm.",
        "three_year_siera": 3.00,
        "games_played_2026": 15,
        "innings_2026": 92.0,
        "notes": "Generational stuff. SIERA suggests ERA could improve. Ceiling is SP1."
    },
    "emmanuel clase": {
        "name": "Emmanuel Clase",
        "team": "CLE",
        "position": "RP",
        "type": "pitcher",
        "stuff_plus": 125,
        "location_plus": 115,
        "siera": 2.50,
        "era": 1.85,
        "k_bb_pct": 22.0,
        "k_per_9": 9.0,
        "whip": 0.85,
        "war": 1.8,
        "adp": 55,
        "injury_history": "Durable. No significant injuries.",
        "three_year_siera": 2.60,
        "saves_2026": 20,
        "games_played_2026": 35,
        "innings_2026": 35.0,
        "notes": "Elite closer. ERA significantly below SIERA - some regression likely but still top RP."
    },
}

# --- Park Factors (2026 updated) ---
PARK_FACTORS = {
    "COL": {"name": "Coors Field", "factor": 114, "note": "Premier hitter's park. Inflates all offensive stats."},
    "CIN": {"name": "Great American Ball Park", "factor": 105, "note": "Hitter-friendly, especially for RHH."},
    "KC": {"name": "Kauffman Stadium", "factor": 103, "note": "2026 UPDATE: Outfield fences pulled in. Now more hitter-friendly than historical average."},
    "NYY": {"name": "Yankee Stadium", "factor": 101, "note": "Short right field porch benefits LHH."},
    "ATL": {"name": "Truist Park", "factor": 100, "note": "Neutral park."},
    "LAD": {"name": "Dodger Stadium", "factor": 97, "note": "Slightly pitcher-friendly."},
    "LAA": {"name": "Angel Stadium", "factor": 96, "note": "Slightly pitcher-friendly."},
    "DET": {"name": "Comerica Park", "factor": 95, "note": "Pitcher-friendly. Spacious outfield."},
    "PIT": {"name": "PNC Park", "factor": 98, "note": "Slightly pitcher-friendly."},
    "CLE": {"name": "Progressive Field", "factor": 99, "note": "Near neutral."},
}

# --- League Format Adjustments ---
LEAGUE_WEIGHTS = {
    "rotisserie": {
        "description": "Rotisserie 5x5 (R, HR, RBI, SB, AVG / W, SV, K, ERA, WHIP)",
        "hitter_priority": ["5-category contributors", "stolen bases premium", "batting average stability"],
        "pitcher_priority": ["saves scarcity", "innings eaters", "ratio anchors (ERA/WHIP)"],
        "notes": "Balance across all categories is key. Don't punt any category."
    },
    "points": {
        "description": "Points League (custom scoring)",
        "hitter_priority": ["OBP/OPS heavy", "extra-base hits", "walks valued"],
        "pitcher_priority": ["strikeouts king", "quality starts", "low walks"],
        "notes": "Ks are typically worth more. Closers less valuable without saves bonus."
    },
    "dynasty": {
        "description": "Dynasty / Keeper League",
        "hitter_priority": ["age curve", "prospect pedigree", "long-term xwOBA trends"],
        "pitcher_priority": ["age and arm health", "stuff+ trajectory", "minor league metrics"],
        "notes": "Weight youth and trajectory heavily. Aging veterans lose value quickly."
    }
}


def _get_current_date_context():
    """Determine season context based on current date."""
    now = datetime.now()
    # MLB season typically runs April - October
    month = now.month
    if month < 4:
        return {"phase": "preseason", "note": "Draft preparation mode. Rely on projections and 3-year rolling averages.", "small_sample": True}
    elif month == 4 and now.day <= 21:
        return {"phase": "early_season", "note": "⚠️ SMALL SAMPLE SIZE WARNING: First 3 weeks of season. Prioritizing 3-year rolling averages over current stats.", "small_sample": True}
    elif month <= 5:
        return {"phase": "april_may", "note": "Early season. Emerging trends but sample size still limited.", "small_sample": False}
    elif month <= 7:
        return {"phase": "midseason", "note": "Sufficient sample size for reliable analysis.", "small_sample": False}
    elif month <= 9:
        return {"phase": "second_half", "note": "Large sample. Second-half splits and fatigue factors matter.", "small_sample": False}
    else:
        return {"phase": "postseason", "note": "Season complete. Evaluating full-year data for dynasty/keeper leagues.", "small_sample": False}


def _analyze_hitter(player_data, league_type, season_context):
    """Perform deep analysis on a hitter."""
    analysis = {
        "player": player_data["name"],
        "team": player_data["team"],
        "position": player_data["position"],
        "analysis_type": "Hitter Evaluation",
    }

    # --- Statcast Triple Threat ---
    xwOBA = player_data["xwOBA"]
    wOBA = player_data["wOBA"]
    barrel_rate = player_data["barrel_rate"]
    sweet_spot = player_data["sweet_spot_pct"]

    # Use 3-year rolling if small sample
    if season_context["small_sample"]:
        effective_xwOBA = player_data.get("three_year_xwOBA", xwOBA)
        effective_wOBA = player_data.get("three_year_wOBA", wOBA)
        analysis["sample_size_note"] = season_context["note"]
    else:
        effective_xwOBA = xwOBA
        effective_wOBA = wOBA

    # --- Regression Risk Analysis ---
    delta = effective_xwOBA - effective_wOBA
    if delta > 0.030:
        regression_tag = "BUY HIGH / BREAKOUT CANDIDATE"
        regression_detail = f"xwOBA ({effective_xwOBA:.3f}) exceeds wOBA ({effective_wOBA:.3f}) by {delta:.3f}. Underlying quality suggests performance should IMPROVE."
    elif delta < -0.030:
        regression_tag = "SELL HIGH / BUST RISK"
        regression_detail = f"wOBA ({effective_wOBA:.3f}) exceeds xwOBA ({effective_xwOBA:.3f}) by {abs(delta):.3f}. Player is OVERPERFORMING underlying metrics. Regression likely."
    else:
        regression_tag = "STABLE PERFORMER"
        regression_detail = f"xwOBA ({effective_xwOBA:.3f}) and wOBA ({effective_wOBA:.3f}) are aligned (delta: {delta:.3f}). Performance is sustainable."

    # --- Barrel Rate Evaluation ---
    barrel_evaluation = ""
    if barrel_rate >= 15:
        barrel_evaluation = f"ELITE ({barrel_rate}%) - Top 3% of league. Premium power profile."
    elif barrel_rate >= 12:
        barrel_evaluation = f"ABOVE AVERAGE ({barrel_rate}%) - Top 15% of league. Solid power contributor."
    elif barrel_rate >= 8:
        barrel_evaluation = f"AVERAGE ({barrel_rate}%) - League average power output."
    else:
        barrel_evaluation = f"BELOW AVERAGE ({barrel_rate}%) - Limited power upside."

    # --- Sweet Spot Evaluation ---
    sweet_spot_eval = ""
    if sweet_spot >= 37:
        sweet_spot_eval = f"ELITE ({sweet_spot}%) - Consistent hard contact in productive launch angles."
    elif sweet_spot >= 34:
        sweet_spot_eval = f"ABOVE AVERAGE ({sweet_spot}%) - Good contact quality."
    elif sweet_spot >= 30:
        sweet_spot_eval = f"AVERAGE ({sweet_spot}%) - League average."
    else:
        sweet_spot_eval = f"BELOW AVERAGE ({sweet_spot}%) - Concerning contact quality."

    # --- Park Factor Analysis ---
    team = player_data["team"]
    park_info = PARK_FACTORS.get(team, {"name": "Unknown", "factor": 100, "note": "No specific park data."})
    park_impact = ""
    if park_info["factor"] >= 108:
        park_impact = f"HIGH BOOST ({park_info['name']}, PF: {park_info['factor']}). {park_info['note']}"
    elif park_info["factor"] >= 102:
        park_impact = f"MODERATE BOOST ({park_info['name']}, PF: {park_info['factor']}). {park_info['note']}"
    elif park_info["factor"] >= 98:
        park_impact = f"NEUTRAL ({park_info['name']}, PF: {park_info['factor']}). {park_info['note']}"
    else:
        park_impact = f"SUPPRESSES OFFENSE ({park_info['name']}, PF: {park_info['factor']}). {park_info['note']}"

    # --- League-Specific Advice ---
    league_info = LEAGUE_WEIGHTS.get(league_type, LEAGUE_WEIGHTS["rotisserie"])

    # --- Fantasy Verdict ---
    score = 0
    # xwOBA tier
    if effective_xwOBA >= 0.400:
        score += 5
    elif effective_xwOBA >= 0.370:
        score += 4
    elif effective_xwOBA >= 0.340:
        score += 3
    elif effective_xwOBA >= 0.310:
        score += 2
    else:
        score += 1

    # Barrel bonus
    if barrel_rate >= 14:
        score += 2
    elif barrel_rate >= 10:
        score += 1

    # Park bonus
    if park_info["factor"] >= 105:
        score += 1

    # Regression adjustment
    if delta > 0.030:
        score += 1  # Breakout potential
    elif delta < -0.030:
        score -= 1  # Bust risk

    # Injury penalty
    injury = player_data.get("injury_history", "")
    if "surgery" in injury.lower() or "tear" in injury.lower() or "HIGH" in injury:
        score -= 1

    if score >= 7:
        verdict = "🟢 MUST START / DRAFT EARLY - Elite fantasy asset."
        action = "Start"
    elif score >= 5:
        verdict = "🟢 START / SOLID DRAFT PICK - Reliable contributor."
        action = "Start"
    elif score >= 3:
        verdict = "🟡 SITUATIONAL START / MID-ROUND VALUE - Matchup dependent."
        action = "Situational"
    else:
        verdict = "🔴 SIT / AVOID - Better options likely available."
        action = "Sit"

    # ADP advice
    adp = player_data.get("adp", 0)
    adp_advice = ""
    if score >= 7 and adp > 20:
        adp_advice = f"SLEEPER ALERT: ADP {adp} is too low. Draft 2-3 rounds early."
    elif score >= 5 and adp > 100:
        adp_advice = f"VALUE PICK: ADP {adp} represents a bargain. Target in mid-rounds."
    elif score <= 3 and adp < 50:
        adp_advice = f"BUST ALERT: ADP {adp} is too high given underlying metrics. Consider fading."
    else:
        adp_advice = f"ADP {adp} is fairly priced for current production level."

    analysis["statcast_metrics"] = {
        "xwOBA": effective_xwOBA,
        "wOBA": effective_wOBA,
        "barrel_rate": barrel_rate,
        "barrel_evaluation": barrel_evaluation,
        "sweet_spot_pct": sweet_spot,
        "sweet_spot_evaluation": sweet_spot_eval,
        "league_percentile_barrel": f"Top {100 - player_data.get('league_pct_barrel', 50)}%" if player_data.get('league_pct_barrel', 50) > 50 else f"{player_data.get('league_pct_barrel', 50)}th percentile"
    }
    analysis["regression_analysis"] = {
        "tag": regression_tag,
        "detail": regression_detail,
        "delta": round(delta, 3)
    }
    analysis["counting_stats_2026"] = {
        "AVG": player_data["avg"],
        "HR": player_data["hr"],
        "RBI": player_data["rbi"],
        "SB": player_data["sb"],
        "OPS": player_data["ops"],
        "WAR": player_data["war"],
        "games_played": player_data.get("games_played_2026", "N/A")
    }
    analysis["park_impact"] = park_impact
    analysis["injury_report"] = player_data.get("injury_history", "No data available.")
    analysis["league_format_advice"] = {
        "format": league_info["description"],
        "priorities": league_info["hitter_priority"],
        "notes": league_info["notes"]
    }
    analysis["adp_analysis"] = adp_advice
    analysis["fantasy_verdict"] = verdict
    analysis["action"] = action
    analysis["additional_notes"] = player_data.get("notes", "")

    return analysis


def _analyze_pitcher(player_data, league_type, season_context):
    """Perform deep analysis on a pitcher."""
    analysis = {
        "player": player_data["name"],
        "team": player_data["team"],
        "position": player_data["position"],
        "analysis_type": "Pitcher Evaluation",
    }

    stuff_plus = player_data.get("stuff_plus", 100)
    location_plus = player_data.get("location_plus", 100)
    siera = player_data.get("siera", 4.00)
    era = player_data.get("era", 4.00)
    k_bb = player_data.get("k_bb_pct", 15.0)

    if season_context["small_sample"]:
        effective_siera = player_data.get("three_year_siera", siera)
        analysis["sample_size_note"] = season_context["note"]
    else:
        effective_siera = siera

    # --- Stuff+ Evaluation ---
    if stuff_plus >= 130:
        stuff_eval = f"ELITE ({stuff_plus}) - Top-tier pitch quality. Dominant stuff."
    elif stuff_plus >= 115:
        stuff_eval = f"ABOVE AVERAGE ({stuff_plus}) - Quality arsenal."
    elif stuff_plus >= 100:
        stuff_eval = f"AVERAGE ({stuff_plus}) - League average stuff."
    else:
        stuff_eval = f"BELOW AVERAGE ({stuff_plus}) - Relies on command over stuff."

    # --- Location+ Evaluation ---
    if location_plus >= 115:
        loc_eval = f"ELITE ({location_plus}) - Exceptional pitch placement."
    elif location_plus >= 105:
        loc_eval = f"ABOVE AVERAGE ({location_plus}) - Good command."
    elif location_plus >= 95:
        loc_eval = f"AVERAGE ({location_plus}) - Adequate command."
    else:
        loc_eval = f"BELOW AVERAGE ({location_plus}) - Command issues."

    # --- SIERA vs ERA ---
    era_delta = era - effective_siera
    if era_delta < -0.30:
        era_analysis = f"ERA ({era:.2f}) is significantly BELOW SIERA ({effective_siera:.2f}). Pitcher is OVERPERFORMING. ERA likely to RISE."
        era_tag = "SELL HIGH"
    elif era_delta > 0.30:
        era_analysis = f"ERA ({era:.2f}) is significantly ABOVE SIERA ({effective_siera:.2f}). Pitcher is UNDERPERFORMING. ERA likely to DROP."
        era_tag = "BUY LOW"
    else:
        era_analysis = f"ERA ({era:.2f}) and SIERA ({effective_siera:.2f}) are aligned. Sustainable performance."
        era_tag = "STABLE"

    # --- K-BB% Evaluation ---
    if k_bb >= 25:
        kbb_eval = f"ELITE ({k_bb}%) - Dominant strikeout-to-walk ratio. Ace-caliber command."
    elif k_bb >= 20:
        kbb_eval = f"ABOVE AVERAGE ({k_bb}%) - Strong command profile."
    elif k_bb >= 15:
        kbb_eval = f"AVERAGE ({k_bb}%) - Adequate but not dominant."
    else:
        kbb_eval = f"BELOW AVERAGE ({k_bb}%) - Walk issues limit upside."

    # --- Reliever Note ---
    is_reliever = player_data["position"] == "RP"
    reliever_note = ""
    if is_reliever:
        reliever_note = "⚠️ RELIEVER VOLATILITY WARNING: Saves are the most volatile category in 2026. Closer roles can change quickly. Monitor committee situations."

    # --- Fantasy Score ---
    score = 0
    if effective_siera <= 2.80:
        score += 5
    elif effective_siera <= 3.20:
        score += 4
    elif effective_siera <= 3.60:
        score += 3
    elif effective_siera <= 4.00:
        score += 2
    else:
        score += 1

    if stuff_plus >= 130:
        score += 2
    elif stuff_plus >= 115:
        score += 1

    if k_bb >= 25:
        score += 2
    elif k_bb >= 20:
        score += 1

    if era_tag == "BUY LOW":
        score += 1
    elif era_tag == "SELL HIGH":
        score -= 1

    injury = player_data.get("injury_history", "")
    if "surgery" in injury.lower() or "tear" in injury.lower() or "strain" in injury.lower():
        score -= 1

    if is_reliever:
        score -= 1  # Reliever discount for volatility

    if score >= 7:
        verdict = "🟢 MUST START / DRAFT AS ACE - Elite fantasy pitcher."
        action = "Start"
    elif score >= 5:
        verdict = "🟢 START / RELIABLE SP2-SP3 - Solid rotation piece."
        action = "Start"
    elif score >= 3:
        verdict = "🟡 MATCHUP DEPENDENT / STREAMING CANDIDATE."
        action = "Situational"
    else:
        verdict = "🔴 SIT / AVOID - High risk, limited reward."
        action = "Sit"

    adp = player_data.get("adp", 0)
    adp_advice = ""
    if score >= 7 and adp > 30:
        adp_advice = f"SLEEPER ALERT: ADP {adp} is too low for this caliber arm. Draft early."
    elif score <= 3 and adp < 50:
        adp_advice = f"BUST ALERT: ADP {adp} is too aggressive. Fade in drafts."
    else:
        adp_advice = f"ADP {adp} is reasonably priced."

    league_info = LEAGUE_WEIGHTS.get(league_type, LEAGUE_WEIGHTS["rotisserie"])

    analysis["pitching_metrics"] = {
        "stuff_plus": stuff_plus,
        "stuff_evaluation": stuff_eval,
        "location_plus": location_plus,
        "location_evaluation": loc_eval,
        "SIERA": effective_siera,
        "ERA": era,
        "era_vs_siera": era_analysis,
        "era_tag": era_tag,
        "K_BB_pct": k_bb,
        "K_BB_evaluation": kbb_eval,
        "K_per_9": player_data.get("k_per_9", "N/A"),
        "WHIP": player_data.get("whip", "N/A")
    }
    analysis["counting_stats_2026"] = {
        "ERA": era,
        "WHIP": player_data.get("whip", "N/A"),
        "WAR": player_data.get("war", "N/A"),
        "games_started": player_data.get("games_played_2026", "N/A"),
        "innings": player_data.get("innings_2026", "N/A"),
        "saves": player_data.get("saves_2026", "N/A")
    }
    analysis["injury_report"] = player_data.get("injury_history", "No data available.")
    if reliever_note:
        analysis["reliever_warning"] = reliever_note
    analysis["league_format_advice"] = {
        "format": league_info["description"],
        "priorities": league_info["pitcher_priority"],
        "notes": league_info["notes"]
    }
    analysis["adp_analysis"] = adp_advice
    analysis["fantasy_verdict"] = verdict
    analysis["action"] = action
    analysis["additional_notes"] = player_data.get("notes", "")

    return analysis


def _get_sleeper_picks(league_type):
    """Identify sleeper picks from the database."""
    sleepers = []
    for key, player in PLAYER_DATABASE.items():
        adp = player.get("adp", 0)
        if player["type"] == "hitter":
            xwOBA = player.get("xwOBA", 0)
            barrel = player.get("barrel_rate", 0)
            if adp > 80 and (xwOBA >= 0.350 or barrel >= 12):
                sleepers.append({
                    "player": player["name"],
                    "team": player["team"],
                    "position": player["position"],
                    "adp": adp,
                    "reason": f"xwOBA: {xwOBA:.3f}, Barrel Rate: {barrel}%. Underlying metrics suggest ADP {adp} is too low.",
                    "park_factor": PARK_FACTORS.get(player["team"], {}).get("factor", 100)
                })
        else:
            siera = player.get("siera", 5.0)
            stuff = player.get("stuff_plus", 100)
            if adp > 80 and (siera <= 3.20 or stuff >= 120):
                sleepers.append({
                    "player": player["name"],
                    "team": player["team"],
                    "position": player["position"],
                    "adp": adp,
                    "reason": f"SIERA: {siera:.2f}, Stuff+: {stuff}. Metrics support a higher draft position."
                })

    sleepers.sort(key=lambda x: x["adp"], reverse=True)
    return sleepers


def _get_bust_candidates():
    """Identify potential bust candidates."""
    busts = []
    for key, player in PLAYER_DATABASE.items():
        adp = player.get("adp", 0)
        if player["type"] == "hitter":
            xwOBA = player.get("xwOBA", 0)
            wOBA = player.get("wOBA", 0)
            injury = player.get("injury_history", "")
            if (wOBA - xwOBA > 0.030) or ("surgery" in injury.lower() and adp < 30):
                busts.append({
                    "player": player["name"],
                    "team": player["team"],
                    "position": player["position"],
                    "adp": adp,
                    "reason": f"wOBA ({wOBA:.3f}) > xwOBA ({xwOBA:.3f}) and/or injury concerns: {injury[:80]}..."
                })
        else:
            era = player.get("era", 5.0)
            siera = player.get("siera", 5.0)
            if era - siera < -0.40 and adp < 50:
                busts.append({
                    "player": player["name"],
                    "team": player["team"],
                    "position": player["position"],
                    "adp": adp,
                    "reason": f"ERA ({era:.2f}) significantly below SIERA ({siera:.2f}). Overperformance likely to regress."
                })

    busts.sort(key=lambda x: x["adp"])
    return busts


def _get_draft_rankings(league_type):
    """Generate overall draft rankings."""
    rankings = []
    season_context = _get_current_date_context()

    for key, player in PLAYER_DATABASE.items():
        if player["type"] == "hitter":
            result = _analyze_hitter(player, league_type, season_context)
        else:
            result = _analyze_pitcher(player, league_type, season_context)

        # Simple scoring for ranking
        score = 0
        if player["type"] == "hitter":
            score += player.get("xwOBA", 0) * 100
            score += player.get("barrel_rate", 0) * 0.5
            score += player.get("war", 0) * 2
            pf = PARK_FACTORS.get(player["team"], {}).get("factor", 100)
            score += (pf - 100) * 0.3
        else:
            score += (5.0 - player.get("siera", 4.0)) * 15
            score += (player.get("stuff_plus", 100) - 100) * 0.2
            score += player.get("k_bb_pct", 15) * 0.3
            score += player.get("war", 0) * 2

        # Injury discount
        injury = player.get("injury_history", "")
        if "surgery" in injury.lower() or "tear" in injury.lower():
            score *= 0.9

        rankings.append({
            "rank": 0,
            "player": player["name"],
            "team": player["team"],
            "position": player["position"],
            "adp": player.get("adp", 999),
            "score": round(score, 2),
            "verdict": result.get("action", "N/A")
        })

    rankings.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(rankings):
        r["rank"] = i + 1

    return rankings


def _compare_matchup(hitter_name, pitcher_name, league_type):
    """Compare a hitter vs pitcher matchup for DFS."""
    hitter = PLAYER_DATABASE.get(hitter_name.lower())
    pitcher = PLAYER_DATABASE.get(pitcher_name.lower())

    if not hitter or hitter["type"] != "hitter":
        return {"error": f"Hitter '{hitter_name}' not found in database."}
    if not pitcher or pitcher["type"] != "pitcher":
        return {"error": f"Pitcher '{pitcher_name}' not found in database."}

    # Simplified matchup analysis
    hitter_score = hitter.get("xwOBA", 0.300) * 100 + hitter.get("barrel_rate", 5) * 0.8
    pitcher_score = (5.0 - pitcher.get("siera", 4.0)) * 10 + (pitcher.get("stuff_plus", 100) - 100) * 0.3

    park = PARK_FACTORS.get(pitcher["team"], {"factor": 100})
    park_adj = (park["factor"] - 100) * 0.5
    hitter_score += park_adj

    if hitter_score > pitcher_score + 5:
        matchup_verdict = f"ADVANTAGE: {hitter['name']}. Favorable matchup for the hitter."
        dfs_recommendation = f"PLAY {hitter['name']} in DFS lineups."
    elif pitcher_score > hitter_score + 5:
        matchup_verdict = f"ADVANTAGE: {pitcher['name']}. Tough matchup for the hitter."
        dfs_recommendation = f"FADE {hitter['name']} against {pitcher['name']} in DFS."
    else:
        matchup_verdict = "NEUTRAL MATCHUP. Could go either way."
        dfs_recommendation = "Slight lean toward the hitter based on overall metrics, but not a strong play."

    return {
        "matchup": f"{hitter['name']} vs {pitcher['name']}",
        "hitter_profile": {
            "name": hitter["name"],
            "xwOBA": hitter["xwOBA"],
            "barrel_rate": hitter["barrel_rate"],
            "matchup_score": round(hitter_score, 2)
        },
        "pitcher_profile": {
            "name": pitcher["name"],
            "SIERA": pitcher.get("siera"),
            "stuff_plus": pitcher.get("stuff_plus"),
            "matchup_score": round(pitcher_score, 2)
        },
        "park_adjustment": park_adj,
        "verdict": matchup_verdict,
        "dfs_recommendation": dfs_recommendation
    }


def execute(args: dict) -> dict:
    """
    MLB Fantasy Baseball Prediction Skill - Entry Point

    Supported actions:
    - "analyze_player": Analyze a specific player. Requires "player" (str). Optional: "league_type" (str).
    - "sleepers": Get sleeper picks. Optional: "league_type" (str).
    - "busts": Get bust candidates.
    - "rankings": Get draft rankings. Optional: "league_type" (str).
    - "matchup": Compare hitter vs pitcher. Requires "hitter" (str) and "pitcher" (str). Optional: "league_type" (str).
    - "park_factors": Get 2026 park factors.
    - "help": Get usage instructions.

    Args:
        args (dict): Dictionary with "action" key and relevant parameters.

    Returns:
        dict: Analysis results.
    """
    try:
        if not isinstance(args, dict):
            return {"error": "Input must be a dictionary with an 'action' key.", "help": "Use action='help' for usage instructions."}

        action = args.get("action", "help").lower().strip()
        league_type = args.get("league_type", "rotisserie").lower().strip()

        if league_type not in LEAGUE_WEIGHTS:
            league_type = "rotisserie"

        season_context = _get_current_date_context()

        if action == "help":
            return {
                "skill": "MLB Fantasy Baseball Prediction Skill",
                "version": "1.0.0",
                "author": "Vishnu (AgentSkillExpert)",
                "supported_actions": {
                    "analyze_player": {
                        "description": "Deep analysis of a specific MLB player for fantasy purposes.",
                        "params": {"player": "Player name (string)", "league_type": "rotisserie|points|dynasty (optional, default: rotisserie)"},
                        "example": {"action": "analyze_player", "player": "Shohei Ohtani", "league_type": "rotisserie"}
                    },
                    "sleepers": {
                        "description": "Get sleeper picks based on underlying metrics vs ADP.",
                        "params": {"league_type": "rotisserie|points|dynasty (optional)"},
                        "example": {"action": "sleepers", "league_type": "dynasty"}
                    },
                    "busts": {
                        "description": "Get bust candidates who are overperforming their underlying metrics.",
                        "example": {"action": "busts"}
                    },
                    "rankings": {
                        "description": "Get overall fantasy draft rankings.",
                        "params": {"league_type": "rotisserie|points|dynasty (optional)"},
                        "example": {"action": "rankings", "league_type": "points"}
                    },
                    "matchup": {
                        "description": "Compare hitter vs pitcher for DFS/daily lineup decisions.",
                        "params": {"hitter": "Hitter name", "pitcher": "Pitcher name"},
                        "example": {"action": "matchup", "hitter": "Aaron Judge", "pitcher": "Tarik Skubal"}
                    },
                    "park_factors": {
                        "description": "Get 2026 park factors for all tracked stadiums.",
                        "example": {"action": "park_factors"}
                    }
                },
                "available_players": list(PLAYER_DATABASE.keys()),
                "league_types": list(LEAGUE_WEIGHTS.keys()),
                "season_context": season_context
            }

        elif action == "analyze_player":
            player_name = args.get("player", "").strip().lower()
            if not player_name:
                return {
                    "error": "Please provide a 'player' name.",
                    "available_players": list(PLAYER_DATABASE.keys()),
                    "example": {"action": "analyze_player", "player": "Shohei Ohtani"}
                }

            player_data = PLAYER_DATABASE.get(player_name)
            if not player_data:
                # Try partial match
                matches = [k for k in PLAYER_DATABASE.keys() if player_name in k or k in player_name]
                if matches:
                    player_data = PLAYER_DATABASE[matches[0]]
                else:
                    return {
                        "error": f"Player '{player_name}' not found in database.",
                        "available_players": list(PLAYER_DATABASE.keys()),
                        "suggestion": "Try a partial name match or check available players list."
                    }

            if player_data["type"] == "hitter":
                result = _analyze_hitter(player_data, league_type, season_context)
            else:
                result = _analyze_pitcher(player_data, league_type, season_context)

            result["season_context"] = season_context
            return {"status": "success", "analysis": result}

        elif action == "sleepers":
            sleepers = _get_sleeper_picks(league_type)
            return {
                "status": "success",
                "league_type": league_type,
                "season_context": season_context,
                "sleeper_picks": sleepers,
                "count": len(sleepers),
                "methodology": "Players with ADP > 80 whose underlying Statcast metrics (xwOBA >= .350 or Barrel Rate >= 12% for hitters; SIERA <= 3.20 or Stuff+ >= 120 for pitchers) suggest they are undervalued."
            }

        elif action == "busts":
            busts = _get_bust_candidates()
            return {
                "status": "success",
                "season_context": season_context,
                "bust_candidates": busts,
                "count": len(busts),
                "methodology": "Players whose surface stats (wOBA/ERA) significantly exceed underlying metrics (xwOBA/SIERA) and/or have concerning injury histories relative to their ADP."
            }

        elif action == "rankings":
            rankings = _get_draft_rankings(league_type)
            return {
                "status": "success",
                "league_type": league_type,
                "season_context": season_context,
                "rankings": rankings,
                "methodology": "Composite score based on xwOBA, Barrel Rate, WAR, Park Factors (hitters) and SIERA, Stuff+, K-BB%, WAR (pitchers). Adjusted for injury history."
            }

        elif action == "matchup":
            hitter_name = args.get("hitter", "").strip()
            pitcher_name = args.get("pitcher", "").strip()
            if not hitter_name or not pitcher_name:
                return {
                    "error": "Both 'hitter' and 'pitcher' names are required.",
                    "example": {"action": "matchup", "hitter": "Aaron Judge", "pitcher": "Tarik Skubal"}
                }
            result = _compare_matchup(hitter_name, pitcher_name, league_type)
            result["season_context"] = season_context
            return {"status": "success", "matchup_analysis": result}

        elif action == "park_factors":
            return {
                "status": "success",
                "season": "2026",
                "park_factors": PARK_FACTORS,
                "note": "Park factors above 100 favor hitters; below 100 favor pitchers. Key 2026 change: Kauffman Stadium (KC) fences pulled in, now 103."
            }

        else:
            return {
                "error": f"Unknown action: '{action}'",
                "supported_actions": ["analyze_player", "sleepers", "busts", "rankings", "matchup", "park_factors", "help"],
                "suggestion": "Use action='help' for detailed usage instructions."
            }

    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": type(e).__name__,
            "suggestion": "Please check your input format and try again. Use action='help' for usage instructions."
        }
