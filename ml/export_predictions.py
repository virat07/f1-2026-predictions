"""
ml/export_predictions.py
Loads trained .joblib models, runs predictions for all 2026 races,
and writes public/ml-predictions.json consumed by the React frontend.

Run standalone: python -m ml.export_predictions
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

_ML_ROOT  = Path(__file__).resolve().parent
_REPO_ROOT = _ML_ROOT.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from config import MODELS_DIR, PROCESSED_DIR, CONSTRUCTORS_2026, DRIVERS_2026

OUTPUT_FILE = _REPO_ROOT / "public" / "ml-predictions.json"

# ── Official 2026 Calendar ────────────────────────────────────────────────────
# Sprint rounds: Chinese, Miami, Canadian, British, Dutch, Singapore
RACES_2026 = [
    {"round": 1,  "name": "Australian Grand Prix",        "circuit": "Albert Park, Melbourne",         "date": "2026-03-15", "sprint": False},
    {"round": 2,  "name": "Chinese Grand Prix",           "circuit": "Shanghai International Circuit",  "date": "2026-03-22", "sprint": True},
    {"round": 3,  "name": "Japanese Grand Prix",          "circuit": "Suzuka Circuit",                  "date": "2026-04-05", "sprint": False},
    {"round": 4,  "name": "Bahrain Grand Prix",           "circuit": "Bahrain International Circuit",   "date": "2026-04-19", "sprint": False},
    {"round": 5,  "name": "Saudi Arabian Grand Prix",     "circuit": "Jeddah Corniche Circuit",         "date": "2026-04-26", "sprint": False},
    {"round": 6,  "name": "Miami Grand Prix",             "circuit": "Miami International Autodrome",   "date": "2026-05-03", "sprint": True},
    {"round": 7,  "name": "Emilia Romagna Grand Prix",    "circuit": "Autodromo Enzo e Dino Ferrari",   "date": "2026-05-17", "sprint": False},
    {"round": 8,  "name": "Monaco Grand Prix",            "circuit": "Circuit de Monaco",               "date": "2026-05-24", "sprint": False},
    {"round": 9,  "name": "Spanish Grand Prix",           "circuit": "Barcelona-Catalunya Grand Prix",  "date": "2026-06-07", "sprint": False},
    {"round": 10, "name": "Canadian Grand Prix",          "circuit": "Circuit Gilles Villeneuve",       "date": "2026-06-14", "sprint": True},
    {"round": 11, "name": "Madrid Grand Prix",            "circuit": "Madrid Street Circuit (IFEMA)",   "date": "2026-06-28", "sprint": False},
    {"round": 12, "name": "Austrian Grand Prix",          "circuit": "Red Bull Ring",                   "date": "2026-07-05", "sprint": False},
    {"round": 13, "name": "British Grand Prix",           "circuit": "Silverstone Circuit",             "date": "2026-07-19", "sprint": True},
    {"round": 14, "name": "Belgian Grand Prix",           "circuit": "Circuit de Spa-Francorchamps",    "date": "2026-08-02", "sprint": False},
    {"round": 15, "name": "Hungarian Grand Prix",         "circuit": "Hungaroring",                     "date": "2026-08-09", "sprint": False},
    {"round": 16, "name": "Dutch Grand Prix",             "circuit": "Circuit Zandvoort",               "date": "2026-08-30", "sprint": True},
    {"round": 17, "name": "Italian Grand Prix",           "circuit": "Autodromo Nazionale Monza",       "date": "2026-09-06", "sprint": False},
    {"round": 18, "name": "Azerbaijan Grand Prix",        "circuit": "Baku City Circuit",               "date": "2026-09-20", "sprint": False},
    {"round": 19, "name": "Singapore Grand Prix",         "circuit": "Marina Bay Street Circuit",       "date": "2026-10-04", "sprint": True},
    {"round": 20, "name": "United States Grand Prix",     "circuit": "Circuit of the Americas",         "date": "2026-10-18", "sprint": False},
    {"round": 21, "name": "Mexican Grand Prix",           "circuit": "Autodromo Hermanos Rodriguez",    "date": "2026-10-25", "sprint": False},
    {"round": 22, "name": "Brazilian Grand Prix",         "circuit": "Autodromo Jose Carlos Pace",      "date": "2026-11-08", "sprint": False},
    {"round": 23, "name": "Las Vegas Grand Prix",         "circuit": "Las Vegas Strip Circuit",         "date": "2026-11-21", "sprint": False},
    {"round": 24, "name": "Abu Dhabi Grand Prix",         "circuit": "Yas Marina Circuit",              "date": "2026-12-06", "sprint": False},
]


# ── 2026 Regulation Reset Factors ────────────────────────────────────────────
# Encodes the competitive impact of the 2026 rule changes per team.
# Each factor is a multiplier applied ON TOP of historical tier estimates.
#
# Key considerations per team:
#   POWER UNIT:
#     Ferrari PU    → Ferrari, Haas, Cadillac  (proven, road-car relevance)
#     Mercedes PU   → Mercedes, McLaren, Williams, Alpine  (strong hybrid expertise)
#     Red Bull Ford → Red Bull Racing, Racing Bulls  (new PU, unknown quantity)
#     Honda PU      → Aston Martin  (strong recent form but new partnership)
#     Audi PU       → Audi  (brand new, steep development curve)
#
#   CHASSIS RESET: Active aero + ground effect removal = teams with best
#     simulation & CFD resources (Ferrari, McLaren, Mercedes) gain most.
#
#   ENERGY MGMT: 50-50 ICE/EV split rewards teams with best software/ERS
#     integration. Mercedes & Ferrari historically best at this.
#
# Scale: 1.0 = no change, >1.0 = regulation benefits team, <1.0 = hurts team
# Sources: Australia + China GP 2026 data, McLaren/Mercedes team principal quotes
# Mercedes ~0.8s clear of field in qualifying; McLaren 0.5-1s off Mercedes pace
REGULATION_RESET_2026 = {
    # Works teams with chassis+PU co-development advantage
    "Mercedes":        1.20,  # Dominant early 2026 — works PU+chassis integration, Russell/Antonelli
    "Ferrari":         1.12,  # 2nd best PU, Hamilton+Leclerc, own works integration — won R1 race
    # Mercedes PU customers — same hardware, big exploitation gap to works team
    "McLaren":         0.95,  # 0.5-1s off Mercedes in Australia/China, PU exploitation deficit
    "Williams":        0.92,  # Mercedes PU customer + Sainz, but chassis lags McLaren
    "Alpine":          0.88,  # Mercedes PU customer, weakest chassis of the three customers
    # Red Bull Ford — new unproven PU, but Verstappen factor
    "Red Bull Racing": 0.90,  # New Ford PU unproven, Verstappen P3 in Australia behind Ferrari
    "Racing Bulls":    0.82,  # Same Ford PU risk, Lawson+Lindblad both relatively unproven
    # Honda PU — strong recent history (2021-2024) but new Aston Martin partnership
    "Aston Martin":    0.80,  # Honda PU new team partnership, Alonso fading, regulation reset hurts
    # Ferrari PU customers
    "Haas":            0.85,  # Ferrari PU customer, Ocon+Bearman solid midfield pairing
    "Cadillac":        0.60,  # Brand new team, Ferrari PU customer, enormous learning curve
    # New works PU — brand new, biggest development curve on grid
    "Audi":            0.68,  # Entirely new PU and team identity, expected 1+ year of development lag
}


def _load_news_sentiment() -> dict:
    sentiment_file = PROCESSED_DIR / "news_sentiment.json"
    if sentiment_file.exists():
        data = json.loads(sentiment_file.read_text())
        return {k: v["sentiment_score"] for k, v in data.get("constructors", {}).items()}
    return {}


def _safe_encode(value: str, mapping: dict, fallback: int = 0) -> int:
    return mapping.get(value, fallback)


def _constructor_form(constructor: str, sentiment: dict) -> dict:
    """
    Estimate 2026 form using 2026-realistic tiers + sentiment adjustment.

    Tier tuple: (expected_wins, expected_podiums, expected_points)
    Reflects 2024 form, 2026 driver moves, and regulation reset.

    Expected 2026 order:
      McLaren > Ferrari > Red Bull > Mercedes >
      Williams > Alpine > Racing Bulls > Aston Martin >
      Haas > Audi > Cadillac
    """
    # Base tiers updated to reflect actual 2026 R1+R2 pecking order:
    # Mercedes >> Ferrari > Red Bull ≈ McLaren > Williams > Racing Bulls >
    # Aston Martin ≈ Alpine > Haas > Audi > Cadillac
    tier = {
        # (wins, podiums, season_points) — 24-race calendar
        "Mercedes":        (12, 22, 580),  # Dominant start, Russell/Antonelli 1-2 pace
        "Ferrari":         (7,  18, 470),  # Won R1, Hamilton+Leclerc, works PU
        "Red Bull Racing": (3,  10, 340),  # Verstappen P3 Australia, Ford PU step back
        "McLaren":         (2,   8, 290),  # 0.5-1s off Mercedes, upgrades due Miami+
        "Williams":        (0,   3, 140),  # Sainz boost but Mercedes customer chassis gap
        "Racing Bulls":    (0,   2, 100),  # Ford PU, Lawson developing
        "Aston Martin":    (0,   1,  85),  # Honda PU new partnership, Alonso/Stroll
        "Alpine":          (0,   1,  80),  # Mercedes PU customer, weakest chassis
        "Haas":            (0,   1,  65),  # Ferrari PU customer, Ocon+Bearman
        "Audi":            (0,   0,  30),  # New works team, development lag
        "Cadillac":        (0,   0,  10),  # Debut season, points a bonus
    }.get(constructor, (0, 1, 45))

    sent       = sentiment.get(constructor, 0.0)
    reg_factor = REGULATION_RESET_2026.get(constructor, 1.0)

    return {
        "cum_wins":    max(0, round((tier[0] + sent * 3)  * reg_factor)),
        "cum_podiums": max(0, round((tier[1] + sent * 5)  * reg_factor)),
        "cum_points":  max(0, round((tier[2] + sent * 80) * reg_factor)),
    }


def predict_race_winner(bundle: dict, race: dict, sentiment: dict) -> list:
    model     = bundle["model"]
    le        = bundle["label_encoder"]
    enc       = bundle["encoder_mapping"]
    event_enc = _safe_encode(race["name"], enc.get("event_name", {}))

    rows = []
    for constructor in CONSTRUCTORS_2026:
        form = _constructor_form(constructor, sentiment)
        row  = pd.DataFrame([{
            "year":            2026,
            "round":           race["round"],
            "event_enc":       event_enc,
            "constructor_enc": _safe_encode(constructor, enc.get("constructor", {})),
            "best_grid":       5,
            **form,
            "avg_grid_pos":    4.0,
        }])
        proba = model.predict_proba(row)[0]
        try:
            class_idx = list(le.classes_).index(constructor)
            win_prob  = float(proba[class_idx])
        except ValueError:
            win_prob  = float(proba.max()) / len(CONSTRUCTORS_2026)
        rows.append({"constructor": constructor, "win_probability": round(win_prob, 4)})

    rows.sort(key=lambda x: x["win_probability"], reverse=True)
    total = sum(r["win_probability"] for r in rows) or 1.0
    for r in rows:
        r["win_probability"] = round(r["win_probability"] / total, 4)
    return rows


def predict_podium(bundle: dict, race: dict, sentiment: dict) -> dict:
    models    = bundle["models"]
    les       = bundle["label_encoders"]
    enc       = bundle["encoder_mapping"]
    event_enc = _safe_encode(race["name"], enc.get("event_name", {}))

    podium = {}
    for i, (model, le) in enumerate(zip(models, les)):
        best_constructor, best_prob = None, -1.0
        for constructor in CONSTRUCTORS_2026:
            form = _constructor_form(constructor, sentiment)
            row  = pd.DataFrame([{
                "year":            2026,
                "round":           race["round"],
                "event_enc":       event_enc,
                "constructor_enc": _safe_encode(constructor, enc.get("constructor", {})),
                "best_grid":       i + 1,
                **form,
                "avg_grid_pos":    float(i + 2),
            }])
            try:
                proba = model.predict_proba(row)[0].max()
            except Exception:
                proba = 0.0
            if proba > best_prob:
                best_prob, best_constructor = proba, constructor
        podium[f"P{i+1}"] = best_constructor
    return podium


# Driver performance split ratios — how constructor points are split between teammates.
# Based on 2024 qualifying head-to-head and historical dominance.
# Must sum to 1.0 per team. Format: {constructor: (driver1_ratio, driver2_ratio)}
# Driver order matches DRIVERS_2026 list in config.py
DRIVER_SPLIT = {
    "McLaren":         (0.54, 0.46),  # Norris slight edge over Piastri
    "Ferrari":         (0.48, 0.52),  # Leclerc home advantage, Hamilton settling in
    "Red Bull Racing": (0.62, 0.38),  # Verstappen dominant over Hadjar (rookie)
    "Mercedes":        (0.58, 0.42),  # Russell experienced, Antonelli is rookie
    "Williams":        (0.52, 0.48),  # Sainz slight edge over Albon
    "Racing Bulls":    (0.55, 0.45),  # Lawson marginal edge over Lindblad (rookie)
    "Aston Martin":    (0.50, 0.50),  # Stroll vs Alonso — Alonso fading, evenly matched
    "Alpine":          (0.52, 0.48),  # Gasly vs Colapinto
    "Haas":            (0.50, 0.50),  # Ocon vs Bearman — new pairing, unknown split
    "Audi":            (0.53, 0.47),  # Hulkenberg experience edge over Bortoleto (rookie)
    "Cadillac":        (0.55, 0.45),  # Perez experience edge over Bottas
}


def predict_season_standings(c_bundle: dict, d_bundle: dict, sentiment: dict) -> dict:
    c_model = c_bundle["model"]
    c_enc   = c_bundle["encoder_mapping"]

    # ── Step 1: Predict constructor points (source of truth) ──────────────────
    constructor_standings = []
    constructor_pts_map = {}  # used to derive driver points below

    for constructor in CONSTRUCTORS_2026:
        form = _constructor_form(constructor, sentiment)
        row  = pd.DataFrame([{
            "year":            2026,
            "constructor_enc": _safe_encode(constructor, c_enc.get("constructor", {})),
            "season_wins":     form["cum_wins"],
            "season_podiums":  form["cum_podiums"],
            "prev_points":     form["cum_points"],
        }])
        pred_pts = round(max(0, float(c_model.predict(row)[0])), 1)
        constructor_pts_map[constructor] = pred_pts
        constructor_standings.append({
            "constructor":      constructor,
            "predicted_points": pred_pts,
        })

    constructor_standings.sort(key=lambda x: x["predicted_points"], reverse=True)
    for i, c in enumerate(constructor_standings):
        c["rank"] = i + 1

    # ── Step 2: Derive driver points from constructor total ───────────────────
    # This ensures driver1_pts + driver2_pts == constructor_pts exactly,
    # fixing the arithmetic inconsistency where independent models disagreed.
    driver_standings = []
    for d in DRIVERS_2026:
        constructor      = d["constructor"]
        constructor_pts  = constructor_pts_map.get(constructor, 0)
        split            = DRIVER_SPLIT.get(constructor, (0.5, 0.5))

        # Find which position (0 or 1) this driver holds within their team
        team_drivers = [x for x in DRIVERS_2026 if x["constructor"] == constructor]
        driver_index = next((i for i, x in enumerate(team_drivers) if x["driver"] == d["driver"]), 0)
        ratio        = split[driver_index] if driver_index < len(split) else 0.5

        driver_pts = round(constructor_pts * ratio, 1)

        driver_standings.append({
            "driver":           d["driver"],
            "name":             d["name"],
            "number":           d["number"],
            "constructor":      constructor,
            "predicted_points": driver_pts,
        })

    driver_standings.sort(key=lambda x: x["predicted_points"], reverse=True)

    # ── Convert points to championship % chance ───────────────────────────────
    # Method: softmax-style normalisation so all 22 drivers sum to 100%
    # Squaring the points before normalising rewards the leader more strongly,
    # giving a more realistic spread (leader ~40%, not just proportional share).
    pts_squared = [max(d["predicted_points"], 0) ** 2 for d in driver_standings]
    total_sq    = sum(pts_squared) or 1.0

    for i, d in enumerate(driver_standings):
        d["position"]        = i + 1
        d["championship_pct"] = round((pts_squared[i] / total_sq) * 100, 1)

    return {"constructors": constructor_standings, "drivers": driver_standings}


def export_predictions():
    print("Loading models ...")
    try:
        winner_bundle = joblib.load(MODELS_DIR / "race_winner.joblib")
        podium_bundle = joblib.load(MODELS_DIR / "podium.joblib")
        c_bundle      = joblib.load(MODELS_DIR / "constructor_standings.joblib")
        d_bundle      = joblib.load(MODELS_DIR / "driver_standings.joblib")
    except FileNotFoundError as e:
        print(f"ERROR: {e}\nRun `python -m ml.train` first.")
        sys.exit(1)

    sentiment = _load_news_sentiment()
    print(f"Sentiment loaded for {len(sentiment)} constructors")

    today = datetime.now(timezone.utc).date()

    print(f"\nGenerating predictions for {len(RACES_2026)} races ...")
    race_predictions = []
    for race in RACES_2026:
        race_date    = datetime.strptime(race["date"], "%Y-%m-%d").date()
        is_completed = race_date < today
        ranked       = predict_race_winner(winner_bundle, race, sentiment)
        podium       = predict_podium(podium_bundle, race, sentiment)

        race_predictions.append({
            "round":             race["round"],
            "name":              race["name"],
            "circuit":           race["circuit"],
            "date":              race["date"],
            "sprint":            race["sprint"],
            "is_completed":      is_completed,
            "predicted_winner":  ranked[0]["constructor"] if ranked else None,
            "win_probabilities": ranked[:5],
            "predicted_podium":  podium,
        })
        status = "done" if is_completed else "pred"
        print(f"  [{status}] R{race['round']:02d} {race['name']:<42} {ranked[0]['constructor'] if ranked else 'N/A'}")

    print("\nGenerating season standings ...")
    standings = predict_season_standings(c_bundle, d_bundle, sentiment)

    output = {
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "season":          2026,
        "source":          "ml_models_fastf1",
        "total_rounds":    len(RACES_2026),
        "sprint_rounds":   [r["round"] for r in RACES_2026 if r["sprint"]],
        "race_predictions": race_predictions,
        "season_standings": standings,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"\n  Saved to {OUTPUT_FILE}")
    print(f"  {len(race_predictions)} races | "
          f"{len(standings['constructors'])} constructors | "
          f"{len(standings['drivers'])} drivers")
    print(f"  Sprint rounds: {output['sprint_rounds']}")


if __name__ == "__main__":
    export_predictions()