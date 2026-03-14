"""
Export model predictions to JSON for the frontend.
Uses 2026 calendar and maps constructors/drivers to model IDs where possible.
Run after train.py:  python -m ml.export_predictions
"""
import sys
import json
from pathlib import Path
import numpy as np
import joblib
import pandas as pd

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))
from config import MODELS_DIR, OUTPUT_DIR
from data.load_data import load_constructors, load_circuits, build_race_results, build_standings_tables

# 2026 calendar: round -> (circuitRef for Ergast, or None for new circuits)
# circuitRef from Ergast; new venues use closest match or "unknown"
CALENDAR_2026 = [
    {"round": 1, "name": "Australian Grand Prix", "circuit": "Albert Park, Melbourne", "circuitRef": "albert_park"},
    {"round": 2, "name": "Chinese Grand Prix", "circuit": "Shanghai International", "circuitRef": "shanghai"},
    {"round": 3, "name": "Japanese Grand Prix", "circuit": "Suzuka", "circuitRef": "suzuka"},
    {"round": 4, "name": "Bahrain Grand Prix", "circuit": "Sakhir", "circuitRef": "bahrain"},
    {"round": 5, "name": "Saudi Arabian Grand Prix", "circuit": "Jeddah Corniche", "circuitRef": "jeddah"},
    {"round": 6, "name": "Miami Grand Prix", "circuit": "Miami International", "circuitRef": "miami"},
    {"round": 7, "name": "Canadian Grand Prix", "circuit": "Circuit Gilles-Villeneuve", "circuitRef": "villeneuve"},
    {"round": 8, "name": "Monaco Grand Prix", "circuit": "Circuit de Monaco", "circuitRef": "monaco"},
    {"round": 9, "name": "Spanish Grand Prix", "circuit": "Barcelona-Catalunya", "circuitRef": "catalunya"},
    {"round": 10, "name": "Austrian Grand Prix", "circuit": "Red Bull Ring", "circuitRef": "red_bull_ring"},
    {"round": 11, "name": "British Grand Prix", "circuit": "Silverstone", "circuitRef": "silverstone"},
    {"round": 12, "name": "Belgian Grand Prix", "circuit": "Spa-Francorchamps", "circuitRef": "spa"},
    {"round": 13, "name": "Hungarian Grand Prix", "circuit": "Hungaroring", "circuitRef": "hungaroring"},
    {"round": 14, "name": "Dutch Grand Prix", "circuit": "Zandvoort", "circuitRef": "zandvoort"},
    {"round": 15, "name": "Italian Grand Prix", "circuit": "Monza", "circuitRef": "monza"},
    {"round": 16, "name": "Madrid Grand Prix", "circuit": "Madrid Street Circuit", "circuitRef": "madrid"},  # new
    {"round": 17, "name": "Azerbaijan Grand Prix", "circuit": "Baku City Circuit", "circuitRef": "baku"},
    {"round": 18, "name": "Singapore Grand Prix", "circuit": "Marina Bay", "circuitRef": "marina_bay"},
    {"round": 19, "name": "United States Grand Prix", "circuit": "COTA, Austin", "circuitRef": "americas"},
    {"round": 20, "name": "Mexican Grand Prix", "circuit": "Autodromo Hermanos Rodriguez", "circuitRef": "rodriguez"},
    {"round": 21, "name": "Brazilian Grand Prix", "circuit": "Interlagos, São Paulo", "circuitRef": "interlagos"},
    {"round": 22, "name": "Las Vegas Grand Prix", "circuit": "Las Vegas Strip", "circuitRef": "vegas"},
    {"round": 23, "name": "Qatar Grand Prix", "circuit": "Lusail International", "circuitRef": "losail"},
    {"round": 24, "name": "Abu Dhabi Grand Prix", "circuit": "Yas Marina", "circuitRef": "yas_marina"},
]

# Map 2026 constructor display names to Ergast constructorRef (for model output)
CONSTRUCTOR_DISPLAY_NAMES = {
    "ferrari": "Scuderia Ferrari",
    "mclaren": "McLaren F1 Team",
    "red_bull": "Oracle Red Bull Racing",
    "mercedes": "Mercedes-AMG Petronas",
    "aston_martin": "Aston Martin Aramco",
    "alpine": "BWT Alpine F1 Team",
    "audi": "Audi F1 Team",           # may map to sauber in history
    "williams": "Williams Racing",
    "haas": "MoneyGram Haas F1",
    "racing_bulls": "Racing Bulls",
    "cadillac": "Cadillac F1 Team",
}


def get_circuit_id_map():
    """circuitRef -> circuitId from Ergast."""
    circuits = load_circuits()
    return dict(zip(circuits["circuitRef"], circuits["circuitId"]))


def get_constructor_id_map():
    """constructorRef -> constructorId, name from Ergast."""
    constructors = load_constructors()
    return (
        dict(zip(constructors["constructorRef"], constructors["constructorId"])),
        dict(zip(constructors["constructorId"], constructors["name"])),
    )


def export_race_predictions():
    """Predict winner and podium for each 2026 race; export to JSON."""
    race_path = MODELS_DIR / "race_winner.joblib"
    podium_path = MODELS_DIR / "podium.joblib"
    if not race_path.exists() or not podium_path.exists():
        print("Run train.py first.")
        return
    race_bundle = joblib.load(race_path)
    podium_bundle = joblib.load(podium_path)
    circuits = load_circuits()
    ref_to_cid = dict(zip(circuits["circuitRef"], circuits["circuitId"]))
    _, cid_to_name = get_constructor_id_map()
    # Build feature row for 2026: year=2026, round, circuitId, mean_grid=10, num_finishers=20
    race_model = race_bundle["model"]
    race_le = race_bundle["label_encoder"]
    enc = race_bundle["encoder_mapping"]
    feature_names = race_bundle["feature_names"]
    podium_models = podium_bundle["models"]
    podium_les = podium_bundle["label_encoders"]

    # circuitId encoding: use same as in training (circuitId from Ergast)
    circuit_enc = enc.get("circuitId", {})
    # If circuit not in training (e.g. madrid), use monza as proxy
    default_cid = list(circuit_enc.keys())[0] if circuit_enc else "1"

    predictions = []
    for race in CALENDAR_2026:
        circuit_ref = race["circuitRef"]
        cid = ref_to_cid.get(circuit_ref)
        if cid is None:
            cid_str = str(default_cid)
        else:
            cid_str = str(cid)
        circuit_encoded = circuit_enc.get(cid_str, circuit_enc.get(default_cid, 0))
        row = np.array([[2026, race["round"], circuit_encoded, 10.0, 20.0]])
        # Ensure feature order
        X = pd.DataFrame(row, columns=feature_names)
        winner_enc = race_model.predict(X)[0]
        winner_ref = race_le.inverse_transform([winner_enc])[0]
        try:
            winner_cid = int(winner_ref)
            winner_name = cid_to_name.get(winner_cid, winner_ref)
        except (ValueError, TypeError):
            winner_name = str(winner_ref)
        # Podium
        p1_enc = podium_models[0].predict(X)[0]
        p2_enc = podium_models[1].predict(X)[0]
        p3_enc = podium_models[2].predict(X)[0]
        def _name(le, enc_val):
            ref = le.inverse_transform([enc_val])[0]
            try:
                return cid_to_name.get(int(ref), ref)
            except (ValueError, TypeError):
                return str(ref)
        p1_name = _name(podium_les[0], p1_enc)
        p2_name = _name(podium_les[1], p2_enc)
        p3_name = _name(podium_les[2], p3_enc)
        predictions.append({
            "round": race["round"],
            "name": race["name"],
            "circuit": race["circuit"],
            "predictedWinner": winner_name,
            "predictedPodium": [p1_name, p2_name, p3_name],
        })

    return predictions


def export_standings():
    """Use standings models to predict 2026 driver and constructor points."""
    driver_path = MODELS_DIR / "driver_standings.joblib"
    ctor_path = MODELS_DIR / "constructor_standings.joblib"
    if not driver_path.exists() or not ctor_path.exists():
        print("Driver/constructor standings models not found. Run train.py.")
        return None, None

    # Load bundles
    driver_bundle = joblib.load(driver_path)
    ctor_bundle = joblib.load(ctor_path)

    driver_model = driver_bundle["model"]
    driver_enc = driver_bundle["encoder_mapping"]
    driver_feats = driver_bundle["feature_names"]

    ctor_model = ctor_bundle["model"]
    ctor_enc = ctor_bundle["encoder_mapping"]
    ctor_feats = ctor_bundle["feature_names"]

    # Helper: reverse mapping from encoded category to original id string
    def invert_mapping(m: dict[str, dict[str, int]]):
        inv = {}
        for col, mm in m.items():
            inv[col] = {v: k for k, v in mm.items()}
        return inv

    driver_inv = invert_mapping(driver_enc)
    ctor_inv = invert_mapping(ctor_enc)

    # Load reference tables
    ds, cs = build_standings_tables()
    drivers_df = ds[["driverId", "forename", "surname"]].drop_duplicates() if ds is not None else None
    ctors_df = cs[["constructorId", "name"]].drop_duplicates() if cs is not None else None

    # --- Constructors ---
    ctor_rows = []
    ctor_cat = ctor_enc.get("constructorId", {})
    for ctor_id_str, enc_val in ctor_cat.items():
        row = np.array([[2026, enc_val]])
        X = pd.DataFrame(row, columns=ctor_feats)
        pts = float(ctor_model.predict(X)[0])
        ctor_id = int(ctor_id_str)
        name = None
        if ctors_df is not None:
            m = ctors_df[ctors_df["constructorId"] == ctor_id]
            if not m.empty:
                name = str(m.iloc[0]["name"])
        ctor_rows.append(
            {
                "constructorId": ctor_id,
                "name": name or f"Constructor {ctor_id}",
                "points": pts,
            }
        )
    ctor_rows.sort(key=lambda r: r["points"], reverse=True)
    constructor_standings = []
    for idx, row in enumerate(ctor_rows, start=1):
        constructor_standings.append(
            {
                "rank": idx,
                "name": row["name"],
                "drivers": "",  # can be filled manually in frontend if desired
                "points": round(row["points"]),
                "color": "#e8002d",  # default; frontend can override
                "note": "ML model prediction",
            }
        )

    # --- Drivers ---
    driver_rows = []
    driver_cat = driver_enc.get("driverId", {})
    for drv_id_str, enc_val in driver_cat.items():
        row = np.array([[2026, enc_val]])
        X = pd.DataFrame(row, columns=driver_feats)
        pts = float(driver_model.predict(X)[0])
        drv_id = int(drv_id_str)
        name = None
        if drivers_df is not None:
            m = drivers_df[drivers_df["driverId"] == drv_id]
            if not m.empty:
                name = f"{m.iloc[0]['forename']} {m.iloc[0]['surname']}"
        driver_rows.append(
            {
                "driverId": drv_id,
                "name": name or f"Driver {drv_id}",
                "points": pts,
                "number": None,
                "team": "",
            }
        )
    driver_rows.sort(key=lambda r: r["points"], reverse=True)

    # Shape for existing UI: top3 (podium) + rest grid
    podium = []
    rest = []
    for idx, row in enumerate(driver_rows, start=1):
        base = {
            "position": idx,
            "name": row["name"],
            "number": row["number"] or idx,
            "team": row["team"] or "",
            "teamClass": "ml",  # generic CSS class
            "points": round(row["points"]),
            "gradient": "linear-gradient(135deg, #ff6b35, #e8002d)",
            "note": "ML model prediction",
        }
        if idx <= 3:
            podium.append(base)
        else:
            rest.append(
                {
                    "pos": idx,
                    "number": base["number"],
                    "color": "#ffffff",
                    "name": base["name"],
                    "team": base["team"],
                    "points": base["points"],
                }
            )

    return podium, rest, constructor_standings


def main():
    race_preds = export_race_predictions()
    podium, rest, ctor = export_standings()

    out = {
        "season": 2026,
        "source": "ml_models",
        "racePredictions": race_preds or [],
        "driverStandings": {
            "podium": podium or [],
            "rest": rest or [],
        },
        "constructorStandings": ctor or [],
    }
    out_path = OUTPUT_DIR / "predictions.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Exported {out_path}")
    return out


if __name__ == "__main__":
    main()
