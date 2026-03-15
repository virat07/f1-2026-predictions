"""
Export model predictions to JSON for the frontend.
Uses 2026 calendar and maps constructors/drivers to model IDs where possible.
Run after train.py:  python -m ml.train
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
from config import MODELS_DIR, OUTPUT_DIR, PROJECT_ROOT
from data.load_data import load_constructors, load_circuits, build_race_results, build_standings_tables, get_2026_teams, get_2026_drivers, load_drivers, get_standardized_name

# 2026 calendar
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
    {"round": 16, "name": "Madrid Grand Prix", "circuit": "Madrid Street Circuit", "circuitRef": "madrid"},
    {"round": 17, "name": "Azerbaijan Grand Prix", "circuit": "Baku City Circuit", "circuitRef": "baku"},
    {"round": 18, "name": "Singapore Grand Prix", "circuit": "Marina Bay", "circuitRef": "marina_bay"},
    {"round": 19, "name": "United States Grand Prix", "circuit": "COTA, Austin", "circuitRef": "americas"},
    {"round": 20, "name": "Mexican Grand Prix", "circuit": "Autodromo Hermanos Rodriguez", "circuitRef": "rodriguez"},
    {"round": 21, "name": "Brazilian Grand Prix", "circuit": "Interlagos, São Paulo", "circuitRef": "interlagos"},
    {"round": 22, "name": "Las Vegas Grand Prix", "circuit": "Las Vegas Strip", "circuitRef": "vegas"},
    {"round": 23, "name": "Qatar Grand Prix", "circuit": "Lusail International", "circuitRef": "losail"},
    {"round": 24, "name": "Abu Dhabi Grand Prix", "circuit": "Yas Marina", "circuitRef": "yas_marina"},
]

def export_race_predictions():
    race_path = MODELS_DIR / "race_winner.joblib"
    podium_path = MODELS_DIR / "podium.joblib"
    if not race_path.exists() or not podium_path.exists():
        return []
    race_bundle = joblib.load(race_path)
    podium_bundle = joblib.load(podium_path)
    circuits = load_circuits()
    ref_to_cid = dict(zip(circuits["circuitRef"], circuits["circuitId"]))
    constructors = load_constructors()
    cid_to_name = dict(zip(constructors["constructorId"], constructors["name"]))
    race_model, race_le, enc, feature_names = race_bundle["model"], race_bundle["label_encoder"], race_bundle["encoder_mapping"], race_bundle["feature_names"]
    podium_models, podium_les = podium_bundle["models"], podium_bundle["label_encoders"]
    circuit_enc = enc.get("circuitId", {})
    default_cid = list(circuit_enc.keys())[0] if circuit_enc else "1"
    predictions = []
    for race in CALENDAR_2026:
        cid = ref_to_cid.get(race["circuitRef"])
        cid_str = str(cid) if cid is not None else str(default_cid)
        row = pd.DataFrame([[2026, race["round"], circuit_enc.get(cid_str, 0), 10.0, 20.0]], columns=feature_names)
        w_enc = race_model.predict(row)[0]
        w_name = cid_to_name.get(int(race_le.inverse_transform([w_enc])[0]), str(race_le.inverse_transform([w_enc])[0]))
        p1 = cid_to_name.get(int(podium_les[0].inverse_transform([podium_models[0].predict(row)[0]])[0]), "")
        p2 = cid_to_name.get(int(podium_les[1].inverse_transform([podium_models[1].predict(row)[0]])[0]), "")
        p3 = cid_to_name.get(int(podium_les[2].inverse_transform([podium_models[2].predict(row)[0]])[0]), "")
        predictions.append({"round": race["round"], "name": race["name"], "circuit": race["circuit"], "predictedWinner": w_name, "predictedPodium": [p1, p2, p3]})
    return predictions

def export_standings():
    driver_path, ctor_path = MODELS_DIR / "driver_standings.joblib", MODELS_DIR / "constructor_standings.joblib"
    if not driver_path.exists() or not ctor_path.exists(): return None, None, None
    db, cb = joblib.load(driver_path), joblib.load(ctor_path)
    active_teams, active_drivers = get_2026_teams(), get_2026_drivers()
    ds, cs = build_standings_tables()
    
    ctor_rows = []
    ctor_enc = cb["encoder_mapping"].get("constructorId", {})
    all_known_constructors = load_constructors()
    
    for name in active_teams:
        std_name = get_standardized_name(name)
        match = all_known_constructors[all_known_constructors["name"] == std_name]
        
        if not match.empty:
            cid = match.iloc[0]["constructorId"]
            cid_str = str(cid)
            if cid_str in ctor_enc:
                X = pd.DataFrame([[2026, ctor_enc[cid_str]]], columns=cb["feature_names"])
                pts = float(cb["model"].predict(X)[0])
                ctor_rows.append({"name": name, "points": max(0, pts)})
            else:
                ctor_rows.append({"name": name, "points": 50.0}) # Conservative fallback
        else:
            ctor_rows.append({"name": name, "points": 10.0})

    ctor_rows.sort(key=lambda x: x["points"], reverse=True)
    constructor_standings = []
    for i, r in enumerate(ctor_rows, 1):
        constructor_standings.append({
            "rank": i,
            "name": r["name"],
            "drivers": "",
            "points": round(r["points"]),
            "color": "#3671C6" if "Red Bull" in r["name"] else "#e8002d",
            "note": "ML Grid Forecast"
        })

    driver_rows = []
    drv_enc = db["encoder_mapping"].get("driverId", {})
    all_known_drivers = load_drivers()
    for dname in active_drivers:
        match = all_known_drivers[all_known_drivers["driver_name"] == dname]
        if not match.empty:
            did = match.iloc[0]["driverId"]
            did_str = str(did)
            if did_str in drv_enc:
                X = pd.DataFrame([[2026, drv_enc[did_str]]], columns=db["feature_names"])
                pts = float(db["model"].predict(X)[0])
                driver_rows.append({"name": dname, "points": max(0, pts)})
            else:
                driver_rows.append({"name": dname, "points": 0.0})
        else:
            driver_rows.append({"name": dname, "points": 0.0})
            
    driver_rows.sort(key=lambda x: x["points"], reverse=True)
    podium = [{"position": i, "name": r["name"], "number": i, "team": "", "teamClass": "ml", "points": round(r["points"]), "gradient": "linear-gradient(135deg, #ff6b35, #e8002d)", "note": "2026 Grid Forecast"} for i, r in enumerate(driver_rows[:3], 1)]
    rest = [{"pos": i, "number": i, "color": "#ffffff", "name": r["name"], "team": "", "points": round(r["points"])} for i, r in enumerate(driver_rows[3:], 4)]
    return podium, rest, constructor_standings

def main():
    race_preds = export_race_predictions()
    podium, rest, ctor = export_standings()
    out = {"season": 2026, "source": "ml_models_v4_standardized", "racePredictions": race_preds or [], "driverStandings": {"podium": podium or [], "rest": rest or []}, "constructorStandings": ctor or []}
    out_path = PROJECT_ROOT / "public" / "ml-predictions.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Exported {out_path} with standardized team mapping.")

if __name__ == "__main__":
    main()
