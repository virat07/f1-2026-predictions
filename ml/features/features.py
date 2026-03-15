"""Build feature matrices and targets for race winner, podium, and standings."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))
from config import MIN_SEASON, MAX_SEASON
from data.load_data import build_race_results, build_standings_tables


def _encode_categorical(df: pd.DataFrame, columns: list) -> tuple[pd.DataFrame, dict]:
    """Label-encode categorical columns; return mapping for inverse transform."""
    mapping = {}
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        uniq = out[col].astype(str).unique()
        mapping[col] = {u: i for i, u in enumerate(uniq)}
        out[col] = out[col].astype(str).map(mapping[col])
    return out, mapping


def build_race_winner_dataset(df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series, dict]:
    """Target: winning constructor per race. Features: circuit, round, season, recent form."""
    if df is None:
        df = build_race_results(MIN_SEASON, MAX_SEASON)
    # One row per race: who won (constructorId)
    winners = df[df["positionOrder"] == 1][["raceId", "year", "round", "circuitId", "constructorId", "constructorRef", "constructor_name"]].copy()
    if winners.empty:
        raise ValueError("No race winners in data")
    # Aggregate race-level features (e.g. mean grid of top teams)
    race_agg = df.groupby("raceId").agg(
        mean_grid=("grid", "mean"),
        num_finishers=("positionOrder", lambda x: (x <= 20).sum()),
    ).reset_index()
    winners = winners.merge(race_agg, on="raceId")
    # Encode circuit and use year/round as numeric
    winners["round"] = pd.to_numeric(winners["round"], errors="coerce").fillna(0)
    X = winners[["year", "round", "circuitId", "mean_grid", "num_finishers"]].copy()
    X, enc = _encode_categorical(X, ["circuitId"])
    y = winners["constructorId"].astype(str)
    return X, y, enc


def build_podium_dataset(df: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list, dict]:
    """Target: top 3 constructor IDs per race (list of 3). Multi-label style."""
    if df is None:
        df = build_race_results(MIN_SEASON, MAX_SEASON)
    races = df[["raceId", "year", "round", "circuitId"]].drop_duplicates()
    podium = df[df["positionOrder"].isin([1, 2, 3])].sort_values(["raceId", "positionOrder"])
    # One row per race with cols: constructor_1st, constructor_2nd, constructor_3rd
    p1 = podium[podium["positionOrder"] == 1][["raceId", "constructorId"]].rename(columns={"constructorId": "p1"})
    p2 = podium[podium["positionOrder"] == 2][["raceId", "constructorId"]].rename(columns={"constructorId": "p2"})
    p3 = podium[podium["positionOrder"] == 3][["raceId", "constructorId"]].rename(columns={"constructorId": "p3"})
    race_agg = df.groupby("raceId").agg(
        mean_grid=("grid", "mean"),
        num_finishers=("positionOrder", lambda x: (x <= 20).sum()),
    ).reset_index()
    merged = races.merge(p1, on="raceId").merge(p2, on="raceId").merge(p3, on="raceId").merge(race_agg, on="raceId")
    merged["round"] = pd.to_numeric(merged["round"], errors="coerce").fillna(0)
    X = merged[["year", "round", "circuitId", "mean_grid", "num_finishers"]].copy()
    X, enc = _encode_categorical(X, ["circuitId"])
    y_list = [merged["p1"].astype(str), merged["p2"].astype(str), merged["p3"].astype(str)]
    return X, y_list, enc


def build_constructor_standings_dataset() -> tuple[pd.DataFrame, pd.Series, dict] | None:
    """Target: end-of-season constructor points. Features: season, constructor."""
    ds, cs = build_standings_tables(MIN_SEASON, MAX_SEASON)
    if cs is None or cs.empty:
        return None
    X = cs[["year", "constructorId"]].copy()
    X, enc = _encode_categorical(X, ["constructorId"])
    y = cs["points"]
    return X, y, enc


def build_driver_standings_dataset() -> tuple[pd.DataFrame, pd.Series, dict] | None:
    """Target: end-of-season driver points."""
    ds, cs = build_standings_tables(MIN_SEASON, MAX_SEASON)
    if ds is None or ds.empty:
        return None
    X = ds[["year", "driverId"]].copy()
    X, enc = _encode_categorical(X, ["driverId"])
    y = ds["points"]
    return X, y, enc
