"""FastF1 Data Loader Module for Pitwall.ai

Provides functions to load and extract F1 session data using the fastf1 library.
All data is cached locally for performance.
"""

import os
import logging
from typing import Optional

import fastf1
import pandas as pd

logger = logging.getLogger(__name__)

# Configure cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def get_event_schedule(year: int) -> pd.DataFrame:
    """Get the full event schedule for a given season.

    Args:
        year: The F1 season year.

    Returns:
        DataFrame with columns: RoundNumber, Country, Location, OfficialEventName,
        EventDate, EventFormat, etc.
    """
    try:
        schedule = fastf1.get_event_schedule(year)
        # Drop the pre-season testing row (round 0) if present
        schedule = schedule[schedule["RoundNumber"] > 0]
        return schedule
    except Exception as e:
        logger.error("Failed to load event schedule for %d: %s", year, e)
        raise


def _load_session(year: int, round_number: int, session_type: str) -> fastf1.core.Session:
    """Internal helper to load and return a fastf1 Session object.

    Args:
        year: Season year.
        round_number: Round number in the calendar.
        session_type: One of 'FP1', 'FP2', 'FP3', 'Q', 'S', 'SS', 'SQ', 'R'.

    Returns:
        A loaded fastf1 Session.
    """
    session = fastf1.get_session(year, round_number, session_type)
    session.load(
        telemetry=True,
        laps=True,
        weather=False,
        messages=False,
    )
    return session


def get_session_results(year: int, round_number: int, session_type: str = "R") -> pd.DataFrame:
    """Get session classification / results.

    Args:
        year: Season year.
        round_number: Round number.
        session_type: Session identifier (default 'R' for Race).

    Returns:
        DataFrame with driver results including Position, Driver, Team, Time, Status, Points.
    """
    try:
        session = _load_session(year, round_number, session_type)
        results = session.results
        if results is None or results.empty:
            return pd.DataFrame()

        cols_to_keep = [
            "DriverNumber", "BroadcastName", "Abbreviation", "TeamName",
            "Position", "ClassifiedPosition", "GridPosition",
            "Time", "Status", "Points",
        ]
        available = [c for c in cols_to_keep if c in results.columns]
        return results[available].reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load session results: %s", e)
        raise


def get_lap_data(
    year: int,
    round_number: int,
    session_type: str = "R",
    driver: Optional[str] = None,
) -> pd.DataFrame:
    """Get lap-by-lap timing data.

    Args:
        year: Season year.
        round_number: Round number.
        session_type: Session identifier.
        driver: Optional 3-letter driver code to filter (e.g. 'VER').

    Returns:
        DataFrame with LapNumber, Driver, LapTime, Sector1/2/3 times,
        Compound, TyreLife, etc.
    """
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps

        if laps is None or laps.empty:
            return pd.DataFrame()

        if driver:
            laps = laps.pick_drivers(driver)

        cols_to_keep = [
            "Driver", "DriverNumber", "LapNumber", "LapTime",
            "Sector1Time", "Sector2Time", "Sector3Time",
            "SpeedI1", "SpeedI2", "SpeedFL", "SpeedST",
            "Compound", "TyreLife", "FreshTyre",
            "Stint", "IsPersonalBest",
        ]
        available = [c for c in cols_to_keep if c in laps.columns]
        df = laps[available].copy()

        # Convert timedelta columns to total seconds for JSON serialization
        for col in ["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]:
            if col in df.columns:
                df[col] = df[col].dt.total_seconds()

        return df.reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load lap data: %s", e)
        raise


def get_telemetry(
    year: int,
    round_number: int,
    driver: str,
    session_type: str = "R",
    lap_number: Optional[int] = None,
) -> pd.DataFrame:
    """Get car telemetry for a specific driver.

    If lap_number is provided, returns telemetry for that lap only.
    Otherwise returns the fastest lap telemetry.

    Args:
        year: Season year.
        round_number: Round number.
        driver: 3-letter driver code (e.g. 'VER').
        session_type: Session identifier.
        lap_number: Optional specific lap number.

    Returns:
        DataFrame with Distance, Speed, Throttle, Brake, nGear, RPM, DRS, X, Y, Z.
    """
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps.pick_drivers(driver)

        if laps.empty:
            return pd.DataFrame()

        if lap_number is not None:
            lap = laps[laps["LapNumber"] == lap_number]
            if lap.empty:
                return pd.DataFrame()
            lap = lap.iloc[0]
        else:
            lap = laps.pick_fastest()

        telemetry = lap.get_telemetry()
        if telemetry is None or telemetry.empty:
            return pd.DataFrame()

        cols_to_keep = [
            "Distance", "Speed", "Throttle", "Brake",
            "nGear", "RPM", "DRS", "X", "Y", "Z",
        ]
        available = [c for c in cols_to_keep if c in telemetry.columns]
        return telemetry[available].reset_index(drop=True)
    except Exception as e:
        logger.error("Failed to load telemetry for %s: %s", driver, e)
        raise


def get_tire_strategy(
    year: int,
    round_number: int,
    session_type: str = "R",
) -> pd.DataFrame:
    """Get tire strategy data for all drivers in a session.

    Returns a DataFrame with one row per stint per driver.

    Args:
        year: Season year.
        round_number: Round number.
        session_type: Session identifier.

    Returns:
        DataFrame with Driver, Stint, Compound, TyreLife (laps on that set),
        StintStartLap, StintEndLap.
    """
    try:
        session = _load_session(year, round_number, session_type)
        laps = session.laps

        if laps is None or laps.empty:
            return pd.DataFrame()

        stints = (
            laps.groupby(["Driver", "Stint", "Compound"])
            .agg(
                StintStartLap=("LapNumber", "min"),
                StintEndLap=("LapNumber", "max"),
                TotalLaps=("LapNumber", "count"),
            )
            .reset_index()
        )
        stints = stints.sort_values(["Driver", "Stint"]).reset_index(drop=True)
        return stints
    except Exception as e:
        logger.error("Failed to load tire strategy: %s", e)
        raise


def get_race_results(year: int, round_number: int) -> pd.DataFrame:
    """Convenience wrapper — returns race classification."""
    return get_session_results(year, round_number, session_type="R")


def get_driver_season_stats(year: int, driver: str) -> dict:
    """Aggregate season statistics for a single driver across all completed rounds.

    Args:
        year: Season year.
        driver: 3-letter driver code.

    Returns:
        Dict with keys: driver, year, races, wins, podiums, poles, points,
        avg_finish, avg_grid, dnfs, fastest_laps.
    """
    try:
        schedule = get_event_schedule(year)
        stats = {
            "driver": driver,
            "year": year,
            "races": 0,
            "wins": 0,
            "podiums": 0,
            "poles": 0,
            "points": 0.0,
            "avg_finish": 0.0,
            "avg_grid": 0.0,
            "dnfs": 0,
            "fastest_laps": 0,
        }
        finishes = []
        grids = []

        for _, event in schedule.iterrows():
            rnd = int(event["RoundNumber"])
            try:
                results = get_session_results(year, rnd, "R")
            except Exception:
                continue  # session not yet available

            if results.empty:
                continue

            drv = results[results["Abbreviation"] == driver]
            if drv.empty:
                continue

            row = drv.iloc[0]
            stats["races"] += 1
            pos = row.get("Position")
            grid = row.get("GridPosition")
            pts = row.get("Points", 0)
            status = str(row.get("Status", ""))

            if pos is not None and not pd.isna(pos):
                pos = int(pos)
                finishes.append(pos)
                if pos == 1:
                    stats["wins"] += 1
                if pos <= 3:
                    stats["podiums"] += 1

            if grid is not None and not pd.isna(grid):
                grids.append(int(grid))
                if int(grid) == 1:
                    stats["poles"] += 1

            stats["points"] += float(pts) if pts and not pd.isna(pts) else 0.0

            if "Finished" not in status and "+" not in status:
                stats["dnfs"] += 1

        if finishes:
            stats["avg_finish"] = round(sum(finishes) / len(finishes), 2)
        if grids:
            stats["avg_grid"] = round(sum(grids) / len(grids), 2)

        return stats
    except Exception as e:
        logger.error("Failed to compute season stats for %s: %s", driver, e)
        raise


def get_drivers_comparison(year: int, drivers: list[str]) -> list[dict]:
    """Compare multiple drivers' season stats side by side.

    Args:
        year: Season year.
        drivers: List of 3-letter driver codes.

    Returns:
        List of stat dicts, one per driver.
    """
    return [get_driver_season_stats(year, d) for d in drivers]
