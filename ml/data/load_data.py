"""
Load and cache F1 race results using the FastF1 library.

FastF1 caches data locally after the first download, so subsequent
runs are fast even without a network connection.
"""
import sys
from pathlib import Path
import pandas as pd
import fastf1

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from config import PROCESSED_DIR, MIN_SEASON, MAX_SEASON

# Tell FastF1 where to store its HTTP cache
_CACHE_DIR = PROCESSED_DIR / "fastf1_cache"
_CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(_CACHE_DIR))

# ── Parquet cache for our processed data ─────────────────────────────────────
_RESULTS_CACHE = PROCESSED_DIR / "race_results.parquet"


def _fetch_season(year: int) -> pd.DataFrame:
    """
    Fetch all race results for *year* from FastF1.
    Returns a tidy DataFrame with one row per (race, constructor).
    """
    print(f"  Fetching season {year} …")
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    rows = []

    for _, event in schedule.iterrows():
        round_num = event.get("RoundNumber", None)
        if round_num is None or round_num == 0:
            continue
        event_name = event.get("EventName", f"Round {round_num}")
        try:
            session = fastf1.get_session(year, round_num, "R")
            session.load(laps=False, telemetry=False, weather=False, messages=False)
        except Exception as exc:
            print(f"    Warning: could not load {year} round {round_num}: {exc}")
            continue

        results = session.results
        if results is None or results.empty:
            continue

        for _, r in results.iterrows():
            rows.append(
                {
                    "year":           year,
                    "round":          round_num,
                    "event_name":     event_name,
                    "driver":         r.get("Abbreviation", "UNK"),
                    "driver_full":    r.get("FullName", "Unknown"),
                    "constructor":    r.get("TeamName", "Unknown"),
                    "grid":           r.get("GridPosition", 0),
                    "position":       r.get("Position", 0),
                    "points":         r.get("Points", 0),
                    "status":         r.get("Status", ""),
                }
            )

    return pd.DataFrame(rows)


def build_race_results(force_refresh: bool = False) -> pd.DataFrame:
    """
    Return a DataFrame of all race results from MIN_SEASON to MAX_SEASON.
    Results are cached locally as a Parquet file.
    """
    if _RESULTS_CACHE.exists() and not force_refresh:
        print(f"Loading cached results from {_RESULTS_CACHE}")
        return pd.read_parquet(_RESULTS_CACHE)

    print(f"Downloading race results {MIN_SEASON}–{MAX_SEASON} via FastF1 …")
    frames = []
    for year in range(MIN_SEASON, MAX_SEASON + 1):
        df = _fetch_season(year)
        if not df.empty:
            frames.append(df)

    if not frames:
        raise RuntimeError("No race data could be fetched. Check your internet connection.")

    all_results = pd.concat(frames, ignore_index=True)
    all_results.to_parquet(_RESULTS_CACHE, index=False)
    print(f"Saved {len(all_results):,} rows to {_RESULTS_CACHE}")
    return all_results