"""
Central configuration for the F1 prediction project.
"""
from pathlib import Path

# ── Directory layout ──────────────────────────────────────────────────────────
_ML_ROOT      = Path(__file__).resolve().parent
MODELS_DIR    = _ML_ROOT / "models"
PROCESSED_DIR = _ML_ROOT / "processed"

MODELS_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# ── Season range ──────────────────────────────────────────────────────────────
MIN_SEASON = 2018   # FastF1 has reliable data from 2018 onwards
MAX_SEASON = 2025   # last fully completed season

# ── Official 2026 F1 Constructor names ───────────────────────────────────────
# Source: FIA 2026 entry list (constructor = sporting identity, no PU suffix)
# 11 teams for the first time since 2016 (Cadillac debut)
CONSTRUCTORS_2026 = [
    "Red Bull Racing",   # RB22  – Red Bull Ford PU
    "Ferrari",           # SF-26 – Ferrari PU
    "Mercedes",          # W17   – Mercedes PU
    "McLaren",           # MCL43 – Mercedes PU
    "Aston Martin",      # AMR26 – Honda PU
    "Alpine",            # A526  – Mercedes PU (switched from Renault)
    "Williams",          # FW48  – Mercedes PU
    "Racing Bulls",      # VCARB 03 – Red Bull Ford PU (formerly AlphaTauri/RB)
    "Haas",              # VF-26 – Ferrari PU
    "Audi",              # R26   – Audi PU (formerly Kick Sauber)
    "Cadillac",          # MAC-26 – Ferrari PU (NEW team, F1 debut)
]

# ── Official 2026 Driver lineup ───────────────────────────────────────────────
# Numbers from FIA entry list (Norris #1 as champion, Verstappen moves to #3)
DRIVERS_2026 = [
    # McLaren
    {"driver": "NOR", "number": 1,  "name": "Lando Norris",        "constructor": "McLaren"},
    {"driver": "PIA", "number": 81, "name": "Oscar Piastri",        "constructor": "McLaren"},
    # Mercedes
    {"driver": "RUS", "number": 63, "name": "George Russell",       "constructor": "Mercedes"},
    {"driver": "ANT", "number": 12, "name": "Andrea Kimi Antonelli","constructor": "Mercedes"},
    # Red Bull Racing
    {"driver": "VER", "number": 3,  "name": "Max Verstappen",       "constructor": "Red Bull Racing"},
    {"driver": "HAD", "number": 6,  "name": "Isack Hadjar",         "constructor": "Red Bull Racing"},
    # Ferrari
    {"driver": "LEC", "number": 16, "name": "Charles Leclerc",      "constructor": "Ferrari"},
    {"driver": "HAM", "number": 44, "name": "Lewis Hamilton",        "constructor": "Ferrari"},
    # Williams
    {"driver": "ALB", "number": 23, "name": "Alexander Albon",      "constructor": "Williams"},
    {"driver": "SAI", "number": 55, "name": "Carlos Sainz",         "constructor": "Williams"},
    # Racing Bulls
    {"driver": "LAW", "number": 30, "name": "Liam Lawson",          "constructor": "Racing Bulls"},
    {"driver": "LIN", "number": 41, "name": "Arvid Lindblad",       "constructor": "Racing Bulls"},
    # Aston Martin
    {"driver": "STR", "number": 18, "name": "Lance Stroll",         "constructor": "Aston Martin"},
    {"driver": "ALO", "number": 14, "name": "Fernando Alonso",      "constructor": "Aston Martin"},
    # Haas
    {"driver": "OCO", "number": 31, "name": "Esteban Ocon",         "constructor": "Haas"},
    {"driver": "BEA", "number": 87, "name": "Oliver Bearman",       "constructor": "Haas"},
    # Audi (formerly Kick Sauber)
    {"driver": "HUL", "number": 27, "name": "Nico Hülkenberg",      "constructor": "Audi"},
    {"driver": "BOR", "number": 5,  "name": "Gabriel Bortoleto",    "constructor": "Audi"},
    # Alpine
    {"driver": "GAS", "number": 10, "name": "Pierre Gasly",         "constructor": "Alpine"},
    {"driver": "COL", "number": 43, "name": "Franco Colapinto",     "constructor": "Alpine"},
    # Cadillac (NEW – debut season)
    {"driver": "PER", "number": 11, "name": "Sergio Pérez",         "constructor": "Cadillac"},
    {"driver": "BOT", "number": 77, "name": "Valtteri Bottas",      "constructor": "Cadillac"},
]