"""Load Ergast CSV tables and return merged DataFrames for modeling."""
import sys
from pathlib import Path
import pandas as pd

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))
from config import RAW_DIR, MIN_SEASON, MAX_SEASON


def _read_csv(name: str) -> pd.DataFrame:
    p = RAW_DIR / f"{name}.csv"
    if not p.exists():
        raise FileNotFoundError(f"Run download_data.py first. Missing: {p}")
    return pd.read_csv(p)


def load_races(season_min: int = MIN_SEASON, season_max: int = MAX_SEASON) -> pd.DataFrame:
    races = _read_csv("races")
    races = races[(races["year"] >= season_min) & (races["year"] <= season_max)]
    return races


def load_results(race_ids: list | None = None) -> pd.DataFrame:
    results = _read_csv("results")
    if race_ids is not None:
        results = results[results["raceId"].isin(race_ids)]
    return results


def load_drivers() -> pd.DataFrame:
    return _read_csv("drivers")


def load_constructors() -> pd.DataFrame:
    return _read_csv("constructors")


def load_circuits() -> pd.DataFrame:
    return _read_csv("circuits")


def load_qualifying(race_ids: list | None = None) -> pd.DataFrame:
    try:
        q = _read_csv("qualifying")
        if race_ids is not None:
            q = q[q["raceId"].isin(race_ids)]
        return q
    except FileNotFoundError:
        return pd.DataFrame()


def build_race_results(season_min: int = MIN_SEASON, season_max: int = MAX_SEASON) -> pd.DataFrame:
    """One row per result: race + driver + constructor + position + points + circuit info."""
    races = load_races(season_min, season_max)
    race_ids = races["raceId"].tolist()
    results = load_results(race_ids)
    drivers = load_drivers()
    constructors = load_constructors()
    circuits = load_circuits()

    # Merge
    df = results.merge(races[["raceId", "year", "round", "circuitId", "name", "date"]], on="raceId")
    df = df.merge(circuits[["circuitId", "circuitRef", "name", "country"]], on="circuitId", suffixes=("_race", "_circuit"))
    df = df.merge(drivers[["driverId", "driverRef", "forename", "surname", "number"]], on="driverId")
    df = df.merge(constructors[["constructorId", "constructorRef", "name"]], on="constructorId", suffixes=("_driver", "_constructor"))
    df["driver_name"] = df["forename"] + " " + df["surname"]
    df["constructor_name"] = df["name_constructor"]

    # Position numeric (handle DNF etc.; CSV may have position or positionOrder)
    pos_col = "positionOrder" if "positionOrder" in df.columns else "position"
    df["positionOrder"] = pd.to_numeric(df[pos_col], errors="coerce").fillna(99).astype(int)
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
    df["grid"] = pd.to_numeric(df["grid"], errors="coerce").fillna(20)

    return df


def build_standings_tables(season_min: int = MIN_SEASON, season_max: int = MAX_SEASON):
    """Load end-of-season driver and constructor standings per season."""
    try:
        ds = _read_csv("driverStandings")
        cs = _read_csv("constructorStandings")
    except FileNotFoundError:
        return None, None
    races = load_races(season_min, season_max)
    # Get last race per season for final standings
    last_races = races.sort_values(["year", "round"]).groupby("year").last().reset_index()[["year", "raceId"]]
    ds = ds.merge(last_races, on="raceId").merge(_read_csv("drivers")[["driverId", "driverRef", "forename", "surname"]], on="driverId")
    cs = cs.merge(last_races, on="raceId").merge(_read_csv("constructors")[["constructorId", "constructorRef", "name"]], on="constructorId")
    return ds, cs
