# F1 Prediction Models (Python)

This folder contains **ML models** that replace the static JSON/JS predictions with data-driven predictions trained on historical F1 data (Ergast).

## Setup

```bash
cd ml
python -m venv venv
source venv/bin/activate   # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 1. Get data

Download the Ergast F1 database (CSV):

```bash
# From project root
python -m ml.data.download_data
```

If the Ergast server is unavailable (503), download the ZIP manually:

- https://ergast.com/downloads/f1db_csv.zip  
- Unzip into `ml/data/raw/` so that `ml/data/raw/results.csv`, `races.csv`, etc. exist.

## 2. Train models

From project root:

```bash
python -m ml.train
```

This trains:

- **Race winner** – classifier (which constructor wins a race given circuit, round, season)
- **Podium** – three classifiers (P1, P2, P3 constructor per race)
- **Constructor standings** – regression (end-of-season constructor points)
- **Driver standings** – regression (end-of-season driver points)

Models are saved under `ml/models/` as `.joblib` files.

## 3. Export predictions for the frontend

```bash
python -m ml.export_predictions
```

Writes `ml/output/predictions.json` with 2026 race-by-race predicted winner and podium (constructor names). You can wire your React app to load this JSON instead of the hardcoded `f1Data.js`, or keep both (e.g. “ML predictions” vs “Editorial”).

## Layout

- `config.py` – paths, seasons, Ergast URL  
- `data/` – download and load Ergast CSV  
- `features/` – feature matrices for each task  
- `models/` – trained `.joblib` models (after training)  
- `train.py` – train all models  
- `export_predictions.py` – 2026 calendar + export to JSON  
- `output/` – generated `predictions.json`

## 2026 calendar and new circuits

The 2026 calendar and circuit names are defined in `export_predictions.py` (`CALENDAR_2026`). New venues (e.g. Madrid) may not exist in Ergast; the exporter falls back to a default circuit encoding so the model still outputs a prediction.

## Using your own data

To use your own CSV instead of Ergast:

1. Put CSVs in `ml/data/raw/` with the same table names as Ergast (`races`, `results`, `drivers`, `constructors`, `circuits`, etc.) and matching column names (at least `raceId`, `year`, `round`, `circuitId`, `constructorId`, `driverId`, `position` or `positionOrder`, `points`, `grid`).
2. Re-run `python -m ml.train` and `python -m ml.export_predictions`.

You can also change `MIN_SEASON` / `MAX_SEASON` in `config.py` to restrict the training window.
