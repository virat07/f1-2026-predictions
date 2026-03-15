"""
Train all F1 prediction models and save them to models/.
Run from project root:  python -m ml.train
Or from ml/:             python train.py
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from config import MODELS_DIR, PROCESSED_DIR, MIN_SEASON, MAX_SEASON
from data.load_data import build_race_results
from features.features import (
    build_race_winner_dataset,
    build_podium_dataset,
    build_constructor_standings_dataset,
    build_driver_standings_dataset,
)


def _year_weights(years: pd.Series, min_w: float = 1.0, max_w: float = 3.0) -> np.ndarray:
    """Linearly upweight recent seasons; max year gets max_w."""
    y = pd.to_numeric(years, errors="coerce").fillna(years.min())
    y_min, y_max = y.min(), y.max()
    if y_max == y_min:
        return np.full(len(y), max_w)
    scaled = (y - y_min) / (y_max - y_min)
    return (min_w + (max_w - min_w) * scaled).to_numpy()


def train_race_winner():
    """Train classifier: race → winning constructor."""
    print("\n[1/4] Training race winner model …")
    X, y, enc = build_race_winner_dataset()
    le = LabelEncoder()
    y_enc = le.fit_transform(y.astype(str))
    X = X.fillna(0)
    sample_w = _year_weights(X["year"])
    X_train, X_test, y_train, y_test, w_train, _ = train_test_split(
        X, y_enc, sample_w, test_size=0.2, random_state=42
    )
    clf = GradientBoostingClassifier(
        n_estimators=150, learning_rate=0.1, max_depth=5, random_state=42
    )
    clf.fit(X_train, y_train, sample_weight=w_train)
    acc = (clf.predict(X_test) == y_test).mean()
    print(f"  ✓ Race winner accuracy (constructor): {acc:.3f}")
    joblib.dump(
        {
            "model": clf,
            "label_encoder": le,
            "encoder_mapping": enc,
            "feature_names": list(X.columns),
        },
        MODELS_DIR / "race_winner.joblib",
    )
    return clf, le, enc


def train_podium():
    """Train three classifiers: P1, P2, P3 constructor per race."""
    print("\n[2/4] Training podium model …")
    X, y_list, enc = build_podium_dataset()
    X = X.fillna(0)
    sample_w = _year_weights(X["year"])
    models, les = [], []
    for i, y in enumerate(y_list):
        le = LabelEncoder()
        y_enc = le.fit_transform(y.astype(str))
        X_train, X_test, y_train, y_test, w_train, _ = train_test_split(
            X, y_enc, sample_w, test_size=0.2, random_state=42
        )
        clf = GradientBoostingClassifier(n_estimators=120, max_depth=4, random_state=42)
        clf.fit(X_train, y_train, sample_weight=w_train)
        acc = (clf.predict(X_test) == y_test).mean()
        print(f"  ✓ Podium P{i+1} accuracy: {acc:.3f}")
        models.append(clf)
        les.append(le)
    joblib.dump(
        {
            "models": models,
            "label_encoders": les,
            "encoder_mapping": enc,
            "feature_names": list(X.columns),
        },
        MODELS_DIR / "podium.joblib",
    )
    return models, les, enc


def train_constructor_standings():
    """Train regression: season + constructor → final points."""
    print("\n[3/4] Training constructor standings model …")
    out = build_constructor_standings_dataset()
    if out is None:
        print("  ⚠ No data – skipping")
        return None
    X, y, enc = out
    X = X.fillna(0)
    sample_w = _year_weights(X["year"])
    X_train, X_test, y_train, y_test, w_train, _ = train_test_split(
        X, y, sample_w, test_size=0.2, random_state=42
    )
    reg = GradientBoostingRegressor(n_estimators=200, max_depth=6, random_state=42)
    reg.fit(X_train, y_train, sample_weight=w_train)
    mae = np.abs(reg.predict(X_test) - y_test).mean()
    print(f"  ✓ Constructor standings MAE: {mae:.1f} points")
    joblib.dump(
        {"model": reg, "encoder_mapping": enc, "feature_names": list(X.columns)},
        MODELS_DIR / "constructor_standings.joblib",
    )
    return reg


def train_driver_standings():
    """Train regression: season + driver → final points."""
    print("\n[4/4] Training driver standings model …")
    out = build_driver_standings_dataset()
    if out is None:
        print("  ⚠ No data – skipping")
        return None
    X, y, enc = out
    X = X.fillna(0)
    sample_w = _year_weights(X["year"])
    X_train, X_test, y_train, y_test, w_train, _ = train_test_split(
        X, y, sample_w, test_size=0.2, random_state=42
    )
    reg = GradientBoostingRegressor(n_estimators=200, max_depth=6, random_state=42)
    reg.fit(X_train, y_train, sample_weight=w_train)
    mae = np.abs(reg.predict(X_test) - y_test).mean()
    print(f"  ✓ Driver standings MAE: {mae:.1f} points")
    joblib.dump(
        {"model": reg, "encoder_mapping": enc, "feature_names": list(X.columns)},
        MODELS_DIR / "driver_standings.joblib",
    )
    return reg


def main():
    print("=" * 60)
    print("  F1 Prediction Model Trainer  (FastF1 + Gradient Boosting)")
    print(f"  Seasons: {MIN_SEASON} – {MAX_SEASON}")
    print("=" * 60)
    train_race_winner()
    train_podium()
    train_constructor_standings()
    train_driver_standings()
    print(f"\n✅  All models saved to {MODELS_DIR}/")
    print("    race_winner.joblib")
    print("    podium.joblib")
    print("    constructor_standings.joblib")
    print("    driver_standings.joblib")


if __name__ == "__main__":
    main()