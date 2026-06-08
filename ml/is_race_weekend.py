import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Define the 2026 calendar directly to avoid importing export_predictions.py
# (which pulls in pandas, numpy, and joblib, which are not installed in the gatekeeper workflow step)
RACES_2026 = [
    {"round": 1,  "name": "Australian Grand Prix",        "date": "2026-03-15"},
    {"round": 2,  "name": "Chinese Grand Prix",           "date": "2026-03-22"},
    {"round": 3,  "name": "Japanese Grand Prix",          "date": "2026-04-05"},
    {"round": 4,  "name": "Bahrain Grand Prix",           "date": "2026-04-19"},
    {"round": 5,  "name": "Saudi Arabian Grand Prix",     "date": "2026-04-26"},
    {"round": 6,  "name": "Miami Grand Prix",             "date": "2026-05-03"},
    {"round": 7,  "name": "Emilia Romagna Grand Prix",    "date": "2026-05-17"},
    {"round": 8,  "name": "Monaco Grand Prix",            "date": "2026-05-24"},
    {"round": 9,  "name": "Spanish Grand Prix",           "date": "2026-06-07"},
    {"round": 10, "name": "Canadian Grand Prix",          "date": "2026-06-14"},
    {"round": 11, "name": "Madrid Grand Prix",            "date": "2026-06-28"},
    {"round": 12, "name": "Austrian Grand Prix",          "date": "2026-07-05"},
    {"round": 13, "name": "British Grand Prix",           "date": "2026-07-19"},
    {"round": 14, "name": "Belgian Grand Prix",           "date": "2026-08-02"},
    {"round": 15, "name": "Hungarian Grand Prix",         "date": "2026-08-09"},
    {"round": 16, "name": "Dutch Grand Prix",             "date": "2026-08-30"},
    {"round": 17, "name": "Italian Grand Prix",           "date": "2026-09-06"},
    {"round": 18, "name": "Azerbaijan Grand Prix",        "date": "2026-09-20"},
    {"round": 19, "name": "Singapore Grand Prix",         "date": "2026-10-04"},
    {"round": 20, "name": "United States Grand Prix",     "date": "2026-10-18"},
    {"round": 21, "name": "Mexican Grand Prix",           "date": "2026-10-25"},
    {"round": 22, "name": "Brazilian Grand Prix",         "date": "2026-11-08"},
    {"round": 23, "name": "Las Vegas Grand Prix",         "date": "2026-11-21"},
    {"round": 24, "name": "Abu Dhabi Grand Prix",         "date": "2026-12-06"},
]

def is_today_race_weekend():
    """
    Check if today is a Friday, Saturday, Sunday, or Monday of a race weekend
    according to the 2026 calendar.
    """
    today = datetime.now(timezone.utc).date()
    print(f"Checking date: {today} (UTC)")

    for race in RACES_2026:
        race_date = datetime.strptime(race["date"], "%Y-%m-%d").date()
        # Friday (race-2) to Monday (race+1) window
        front_window = race_date - timedelta(days=2)
        end_window   = race_date + timedelta(days=1)
        
        if front_window <= today <= end_window:
            print(f"🏁 Today is within the {race['name']} weekend! ({front_window} to {end_window})")
            return True

    print("🛑 Today is a non-race day. Skipping automation.")
    return False

if __name__ == "__main__":
    if is_today_race_weekend():
        sys.exit(0)  # Success = continue workflow
    else:
        sys.exit(1)  # Failure = stop workflow
