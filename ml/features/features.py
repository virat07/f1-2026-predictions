"""
Feature engineering for all four F1 prediction tasks.

Each builder returns (X, y, encoder_mapping) where:
  X               – pd.DataFrame of numeric features
  y / y_list      – target(s)
  encoder_mapping – dict of {column: {original_value: int_code}}
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

# ✅ FIX: Import REG_IMPACT and PROCESSED_DIR for feature enrichment
from config import CONSTRUCTORS_2026, REG_IMPACT_2026, PROCESSED_DIR
from data.load_data import build_race_results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_sentiment() -> Dict[str, float]:
    """Load latest news sentiment scores by constructor."""
    path = PROCESSED_DIR / "news_sentiment.json"
    if not path.exists():
        return {c: 0.0 for c in CONSTRUCTORS_2026}
    try:
        data = json.loads(path.read_text())["constructors"]
        return {c: data.get(c, {}).get("sentiment_score", 0.0) for c in CONSTRUCTORS_2026}
    except:
        return {c: 0.0 for c in CONSTRUCTORS_2026}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _encode_col(series: pd.Series) -> Tuple[pd.Series, Dict]:
    """Label-encode a string column; return encoded series + mapping dict."""
    cats = pd.Categorical(series)
    mapping = {v: i for i, v in enumerate(cats.categories)}
    return pd.Series(cats.codes, index=series.index), mapping


def _constructor_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (year, round, constructor) row, compute rolling stats up to but
    NOT including the current race (to avoid leakage):
      - cum_wins        : wins so far this season
      - cum_podiums     : podium finishes so far
      - cum_points      : points accumulated so far
      - avg_grid_pos    : average qualifying position this season
    """
    df = df.sort_values(["year", "round"])
    df["is_win"]    = (df["position"] == 1).astype(int)
    df["is_podium"] = (df["position"] <= 3).astype(int)

    sentiment_map = _load_sentiment()

    stats_list = []
    for (year, constructor), grp in df.groupby(["year", "constructor"]):
        grp = grp.sort_values("round").copy()
        grp["cum_wins"]     = grp["is_win"].cumsum().shift(1).fillna(0)
        grp["cum_podiums"]  = grp["is_podium"].cumsum().shift(1).fillna(0)
        grp["cum_points"]   = grp["points"].cumsum().shift(1).fillna(0)
        grp["avg_grid_pos"] = grp["grid"].expanding().mean().shift(1).fillna(grp["grid"].mean())

        # ✅ FIX: Inject 2026 Regulation Impact
        if year >= 2026:
            grp["reg_impact"] = REG_IMPACT_2026.get(constructor, 0.0)
            grp["sentiment"]  = sentiment_map.get(constructor, 0.0)
        else:
            # Baseline zero for historical data where impact is already "baked into" results
            grp["reg_impact"] = 0.0
            grp["sentiment"]  = 0.0

        stats_list.append(grp)

    return pd.concat(stats_list).sort_index()


def _race_level_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse driver-level rows to one row per (year, round, constructor),
    keeping the best-placed driver's grid position and the sum of points.
    """
    agg = (
        df.groupby(["year", "round", "event_name", "constructor"])
        .agg(
            best_position=("position", "min"),
            best_grid=("grid", "min"),
            total_points=("points", "sum"),
        )
        .reset_index()
    )
    return agg


# ── Dataset builders ──────────────────────────────────────────────────────────

def build_race_winner_dataset():
    """
    Pointwise approach: One row per (race, constructor).
    Target = 1 if that constructor won, else 0.
    """
    raw = build_race_results()
    df  = _constructor_stats(raw)
    agg = _race_level_features(df)

    # Merge rolling stats back
    agg = agg.merge(
        df[["year", "round", "constructor", "cum_wins", "cum_podiums",
            "cum_points", "avg_grid_pos", "reg_impact", "sentiment"]].drop_duplicates(["year", "round", "constructor"]),
        on=["year", "round", "constructor"],
        how="left",
    )

    # Identify winner per race
    winners = (
        agg.sort_values("best_position")
           .groupby(["year", "round"])
           .first()
           .reset_index()[["year", "round", "constructor"]]
           .rename(columns={"constructor": "winner_name"})
    )
    agg = agg.merge(winners, on=["year", "round"])
    agg["is_winner"] = (agg["constructor"] == agg["winner_name"]).astype(int)

    enc = {}
    agg["event_enc"], enc["event_name"]       = _encode_col(agg["event_name"])
    agg["constructor_enc"], enc["constructor"] = _encode_col(agg["constructor"])

    feature_cols = [
        "year", "round", "event_enc", "constructor_enc",
        "best_grid", "cum_wins", "cum_podiums", "cum_points", "avg_grid_pos",
        "reg_impact", "sentiment"
    ]
    X = agg[feature_cols].copy().reset_index(drop=True)
    y = agg["is_winner"].copy().reset_index(drop=True)
    return X, y, enc


def build_podium_dataset():
    """
    Pointwise approach: One row per (race, constructor).
    Target y_list = [is_p1, is_p2, is_p3].
    """
    raw = build_race_results()
    df  = _constructor_stats(raw)
    agg = _race_level_features(df)

    agg = agg.merge(
        df[["year", "round", "constructor", "cum_wins", "cum_podiums",
            "cum_points", "avg_grid_pos", "reg_impact", "sentiment"]].drop_duplicates(["year", "round", "constructor"]),
        on=["year", "round", "constructor"],
        how="left",
    )

    enc = {}
    agg["event_enc"], enc["event_name"]       = _encode_col(agg["event_name"])
    agg["constructor_enc"], enc["constructor"] = _encode_col(agg["constructor"])

    # Map positions
    agg["is_p1"] = (agg["best_position"] == 1).astype(int)
    agg["is_p2"] = (agg["best_position"] == 2).astype(int)
    agg["is_p3"] = (agg["best_position"] == 3).astype(int)

    feature_cols = [
        "year", "round", "event_enc", "constructor_enc",
        "best_grid", "cum_wins", "cum_podiums", "cum_points", "avg_grid_pos",
        "reg_impact", "sentiment"
    ]
    X      = agg[feature_cols].copy().reset_index(drop=True)
    y_list = [agg["is_p1"].reset_index(drop=True),
              agg["is_p2"].reset_index(drop=True),
              agg["is_p3"].reset_index(drop=True)]
    return X, y_list, enc


def build_constructor_standings_dataset():
    """
    One row per (season, constructor).  Target = total season points.
    Uses only historical seasons (no current-season leakage).
    """
    raw = build_race_results()
    if raw.empty:
        return None

    season_pts = (
        raw.groupby(["year", "constructor"])["points"]
           .sum()
           .reset_index()
           .rename(columns={"points": "total_points"})
    )

    # Features: prior season points (lag-1) + win/podium counts
    win_counts = (
        raw[raw["position"] == 1]
           .groupby(["year", "constructor"])
           .size()
           .reset_index(name="season_wins")
    )
    podium_counts = (
        raw[raw["position"] <= 3]
           .groupby(["year", "constructor"])
           .size()
           .reset_index(name="season_podiums")
    )

    df = season_pts.merge(win_counts,    on=["year", "constructor"], how="left")
    df = df.merge(podium_counts,         on=["year", "constructor"], how="left")
    df = df.fillna(0)

    enc = {}
    df["constructor_enc"], enc["constructor"] = _encode_col(df["constructor"])

    # Lag-1 points
    df = df.sort_values(["constructor", "year"])
    df["prev_points"] = df.groupby("constructor")["total_points"].shift(1).fillna(0)

    # ✅ FIX: Inject 2026 Enrichment
    sentiment_map = _load_sentiment()
    df["reg_impact"] = df.apply(lambda r: REG_IMPACT_2026.get(r["constructor"], 0.0) if r["year"] >= 2026 else 0.0, axis=1)
    df["sentiment"]  = df.apply(lambda r: sentiment_map.get(r["constructor"], 0.0) if r["year"] >= 2026 else 0.0, axis=1)

    feature_cols = ["year", "constructor_enc", "season_wins", "season_podiums", "prev_points", "reg_impact", "sentiment"]
    X = df[feature_cols].reset_index(drop=True)
    y = df["total_points"].reset_index(drop=True)
    return X, y, enc


def build_driver_standings_dataset():
    """
    One row per (season, driver).  Target = total season points.
    """
    raw = build_race_results()
    if raw.empty:
        return None

    season_pts = (
        raw.groupby(["year", "driver"])["points"]
           .sum()
           .reset_index()
           .rename(columns={"points": "total_points"})
    )

    win_counts = (
        raw[raw["position"] == 1]
           .groupby(["year", "driver"])
           .size()
           .reset_index(name="season_wins")
    )
    podium_counts = (
        raw[raw["position"] <= 3]
           .groupby(["year", "driver"])
           .size()
           .reset_index(name="season_podiums")
    )

    df = season_pts.merge(win_counts,   on=["year", "driver"], how="left")
    df = df.merge(podium_counts,        on=["year", "driver"], how="left")
    df = df.fillna(0)

    enc = {}
    df["driver_enc"], enc["driver"] = _encode_col(df["driver"])

    df = df.sort_values(["driver", "year"])
    df["prev_points"] = df.groupby("driver")["total_points"].shift(1).fillna(0)

    # ✅ FIX: Inject 2026 Enrichment (linked via Constructor)
    from config import DRIVERS_2026
    driver_team_map = {d["name"]: d["constructor"] for d in DRIVERS_2026}
    sentiment_map   = _load_sentiment()

    def get_driver_impact(row):
        if row["year"] < 2026: return 0.0
        team = driver_team_map.get(row["driver"], "") # Note: df has 'driver' alias but we need to map to full name or constructor
        # Wait, the df["driver"] is likely the 3-letter alias. I should handle that.
        return 0.0 # simplified for now, or I search by alias

    # Let's use a more robust mapping for drivers
    alias_to_team = {d["driver"]: d["constructor"] for d in DRIVERS_2026}
    df["reg_impact"] = df.apply(lambda r: REG_IMPACT_2026.get(alias_to_team.get(r["driver"]), 0.0) if r["year"] >= 2026 else 0.0, axis=1)
    df["sentiment"]  = df.apply(lambda r: sentiment_map.get(alias_to_team.get(r["driver"]), 0.0) if r["year"] >= 2026 else 0.0, axis=1)

    feature_cols = ["year", "driver_enc", "season_wins", "season_podiums", "prev_points", "reg_impact", "sentiment"]
    X = df[feature_cols].reset_index(drop=True)
    y = df["total_points"].reset_index(drop=True)
    return X, y, enc