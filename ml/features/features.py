"""
Feature engineering for all four F1 prediction tasks.

Each builder returns (X, y, encoder_mapping) where:
  X               – pd.DataFrame of numeric features
  y / y_list      – target(s)
  encoder_mapping – dict of {column: {original_value: int_code}}
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from config import CONSTRUCTORS_2026
from data.load_data import build_race_results


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

    stats_list = []
    for (year, constructor), grp in df.groupby(["year", "constructor"]):
        grp = grp.sort_values("round").copy()
        grp["cum_wins"]     = grp["is_win"].cumsum().shift(1).fillna(0)
        grp["cum_podiums"]  = grp["is_podium"].cumsum().shift(1).fillna(0)
        grp["cum_points"]   = grp["points"].cumsum().shift(1).fillna(0)
        grp["avg_grid_pos"] = grp["grid"].expanding().mean().shift(1).fillna(grp["grid"].mean())
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
    One row per race.  Target = winning constructor name.
    Features: year, round, encoded event, encoded constructor, rolling stats.
    """
    raw = build_race_results()
    df  = _constructor_stats(raw)
    agg = _race_level_features(df)

    # Merge rolling stats back
    agg = agg.merge(
        df[["year", "round", "constructor", "cum_wins", "cum_podiums",
            "cum_points", "avg_grid_pos"]].drop_duplicates(["year", "round", "constructor"]),
        on=["year", "round", "constructor"],
        how="left",
    )

    # Identify winner per race
    winners = (
        agg.sort_values("best_position")
           .groupby(["year", "round"])
           .first()
           .reset_index()[["year", "round", "constructor"]]
           .rename(columns={"constructor": "winner"})
    )
    agg = agg.merge(winners, on=["year", "round"])

    # Keep one row per race (use the winner's row for simplicity)
    race_df = (
        agg[agg["constructor"] == agg["winner"]]
        .drop_duplicates(["year", "round"])
        .copy()
    )

    enc = {}
    race_df["event_enc"], enc["event_name"] = _encode_col(race_df["event_name"])
    race_df["constructor_enc"], enc["constructor"] = _encode_col(race_df["constructor"])

    feature_cols = [
        "year", "round", "event_enc", "constructor_enc",
        "best_grid", "cum_wins", "cum_podiums", "cum_points", "avg_grid_pos",
    ]
    X = race_df[feature_cols].reset_index(drop=True)
    y = race_df["winner"].reset_index(drop=True)
    return X, y, enc


def build_podium_dataset():
    """
    One row per race.  Targets = [P1_constructor, P2_constructor, P3_constructor].
    """
    raw = build_race_results()
    df  = _constructor_stats(raw)
    agg = _race_level_features(df)

    agg = agg.merge(
        df[["year", "round", "constructor", "cum_wins", "cum_podiums",
            "cum_points", "avg_grid_pos"]].drop_duplicates(["year", "round", "constructor"]),
        on=["year", "round", "constructor"],
        how="left",
    )

    enc = {}
    agg["event_enc"], enc["event_name"]       = _encode_col(agg["event_name"])
    agg["constructor_enc"], enc["constructor"] = _encode_col(agg["constructor"])

    podium_list = []
    for pos in [1, 2, 3]:
        pos_df = (
            agg.sort_values("best_position")
               .groupby(["year", "round"])
               .nth(pos - 1)          # 0-indexed
               .reset_index()[["year", "round", "constructor"]]
               .rename(columns={"constructor": f"P{pos}"})
        )
        podium_list.append(pos_df)

    base = podium_list[0]
    for p in podium_list[1:]:
        base = base.merge(p, on=["year", "round"])

    # Use winner rows for features
    winner_feats = (
        agg.sort_values("best_position")
           .groupby(["year", "round"])
           .first()
           .reset_index()
    )
    merged = winner_feats.merge(base, on=["year", "round"])

    feature_cols = [
        "year", "round", "event_enc", "constructor_enc",
        "best_grid", "cum_wins", "cum_podiums", "cum_points", "avg_grid_pos",
    ]
    X      = merged[feature_cols].reset_index(drop=True)
    y_list = [merged["P1"].reset_index(drop=True),
              merged["P2"].reset_index(drop=True),
              merged["P3"].reset_index(drop=True)]
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

    feature_cols = ["year", "constructor_enc", "season_wins", "season_podiums", "prev_points"]
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

    feature_cols = ["year", "driver_enc", "season_wins", "season_podiums", "prev_points"]
    X = df[feature_cols].reset_index(drop=True)
    y = df["total_points"].reset_index(drop=True)
    return X, y, enc