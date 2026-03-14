"""Paths and settings for F1 ML pipeline."""
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "output"

# Ensure dirs exist
for d in (RAW_DIR, PROCESSED_DIR, MODELS_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Ergast CSV (historical F1 data)
ERGAST_CSV_URL = "https://ergast.com/downloads/f1db_csv.zip"
ERGAST_ZIP_PATH = RAW_DIR / "f1db_csv.zip"

# Training config
MIN_SEASON = 2014   # Modern hybrid era
MAX_SEASON = 2024   # Latest in Ergast
TARGET_SEASON = 2026
