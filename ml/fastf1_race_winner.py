"""Train a FastF1-based race winner model and update public/ml-predictions.json."""

from __future__ import annotations

import json
from pathlib import Path

import fastf1
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split


CACHE_DIR = Path.home() / ".fastf1-cache"
SEASONS = list(range(2018, 2027))
TARGET_SEASON = 2026

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_JSON = PROJECT_ROOT / "public" / "ml-predictions.json"


CALENDAR_2026 = [
    {"round": 1, "name": "Australian Grand Prix", "circuit": "Albert Park, Melbourne"},
    {"round": 2, "name": "Chinese Grand Prix", "circuit": "Shanghai International"},
    {"round": 3, "name": "Japanese Grand Prix", "circuit": "Suzuka"},
    {"round": 4, "name": "Bahrain Grand Prix", "circuit": "Sakhir"},
    {"round": 5, "name": "Saudi Arabian Grand Prix", "circuit": "Jeddah Corniche"},
    {"round": 6, "name": "Miami Grand Prix", "circuit": "Miami International"},
    {"round": 7, "name": "Canadian Grand Prix", "circuit": "Circuit Gilles-Villeneuve"},
    {"round": 8, "name": "Monaco Grand Prix", "circuit": "Circuit de Monaco"},
    {"round": 9, "name": "Spanish Grand Prix", "circuit": "Barcelona-Catalunya"},
    {"round": 10, "name": "Austrian Grand Prix", "circuit": "Red Bull Ring"},
    {"round": 11, "name": "British Grand Prix", "circuit": "Silverstone"},
    {"round": 12, "name": "Belgian Grand Prix", "circuit": "Spa-Francorchamps"},
    {"round": 13, "name": "Hungarian Grand Prix", "circuit": "Hungaroring"},
    {"round": 14, "name": "Dutch Grand Prix", "circuit": "Zandvoort"},
    {"round": 15, "name": "Italian Grand Prix", "circuit": "Monza"},
    {"round": 16, "name": "Madrid Grand Prix", "circuit": "Madrid Street Circuit"},
    {"round": 17, "name": "Azerbaijan Grand Prix", "circuit": "Baku City Circuit"},
    {"round": 18, "name": "Singapore Grand Prix", "circuit": "Marina Bay"},
    {"round": 19, "name": "United States Grand Prix", "circuit": "COTA, Austin"},
    {"round": 20, "name": "Mexican Grand Prix", "circuit": "Autodromo Hermanos Rodriguez"},
    {"round": 21, "name": "Brazilian Grand Prix", "circuit": "Interlagos, São Paulo"},
    {"round": 22, "name": "Las Vegas Grand Prix", "circuit": "Las Vegas Strip"},
    {"round": 23, "name": "Qatar Grand Prix", "circuit": "Lusail International"},
    {"round": 24, "name": "Abu Dhabi Grand Prix", "circuit": "Yas Marina"},
]


def enable_cache() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))


def build_training_data() -> pd.DataFrame:
    """Build simple per-race dataset with winner team and a few features."""
    rows: list[dict] = []
    for year in SEASONS:
        rnd = 1
        while True:
            try:
                session = fastf1.get_session(year, rnd, "Race")
            except Exception:
                break
            try:
                session.load(telemetry=False, weather=False, messages=False)
            except Exception:
                rnd += 1
                continue

            res = session.results
            if res is None or res.empty:
                rnd += 1
                continue

            winner = res[res["Position"] == 1]
            if winner.empty:
                rnd += 1
                continue
            w = winner.iloc[0]

            circuit_name = str(session.event["EventName"])
            rows.append(
                {
                    "year": year,
                    "round": rnd,
                    "circuit_len": len(circuit_name),
                    "winner_team": w.TeamName,
                }
            )
            rnd += 1

    return pd.DataFrame(rows)


def encode_and_train(df: pd.DataFrame):
    teams = df["winner_team"].astype("category")
    df["winner_label"] = teams.cat.codes
    label_to_team = dict(enumerate(teams.cat.categories))

    X = df[["year", "round", "circuit_len"]].astype(float)
    y = df["winner_label"].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    clf = GradientBoostingClassifier(random_state=42)
    clf.fit(X_train, y_train)
    acc = float((clf.predict(X_test) == y_test).mean())
    print(f"Race winner model accuracy (holdout): {acc:.3f}")
    return clf, label_to_team


def predict_2026_races(clf, label_to_team: dict[int, str]):
    sentiment_path = PROJECT_ROOT / "ml" / "output" / "team_sentiment.json"
    sentiments = {}
    if sentiment_path.exists():
        with open(sentiment_path) as f:
            sentiments = json.load(f)
            
    # Inject user's specific feedback about F1 news momentum
    sentiments["Ferrari"] = sentiments.get("Ferrari", 0) + 1.2
    sentiments["McLaren"] = sentiments.get("McLaren", 0) + 1.2

    preds: list[dict] = []
    for race in CALENDAR_2026:
        X_row = np.array(
            [[TARGET_SEASON, race["round"], len(race["circuit"])]], dtype=float
        )
        # Use probabilities instead of absolute winner
        probas = clf.predict_proba(X_row)[0]
        
        # Apply off-track sentiment modifiers
        adj_probas = probas.copy()
        for i, team in label_to_team.items():
            if "Ferrari" in team:
                boost = sentiments.get("Ferrari", 0.0)
            elif "McLaren" in team:
                boost = sentiments.get("McLaren", 0.0)
            else:
                boost = sentiments.get(team, 0.0)
                
            if boost > 0:
                adj_probas[i] *= (1 + boost)
            elif boost < 0:
                adj_probas[i] *= max(0.1, (1 + boost * 0.5))
                
        # Normalize
        adj_probas /= adj_probas.sum()
            
        # Add dynamic chaos by sampling according to weighted probabilities!
        label = np.random.choice(len(label_to_team), p=adj_probas)
        team = label_to_team.get(label, "Unknown Team")
        
        preds.append(
            {
                "round": race["round"],
                "name": race["name"],
                "circuit": race["circuit"],
                "predictedWinner": team,
                "predictedPodium": [],
            }
        )
    return preds


def write_to_public(pred_races: list[dict]) -> None:
    PUBLIC_JSON.parent.mkdir(parents=True, exist_ok=True)
    if PUBLIC_JSON.exists():
        data = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    else:
        data = {}
    data["season"] = TARGET_SEASON
    data["source"] = "fastf1_race_winner"
    data["racePredictions"] = pred_races
    PUBLIC_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Updated", PUBLIC_JSON)


def main() -> None:
    enable_cache()
    df = build_training_data()
    print(f"Built dataset with {len(df)} races from {min(SEASONS)}–{max(SEASONS)}")
    if df.empty:
        print("No training data built; aborting.")
        return
    clf, label_to_team = encode_and_train(df)
    pred_races = predict_2026_races(clf, label_to_team)
    write_to_public(pred_races)


if __name__ == "__main__":
    main()

