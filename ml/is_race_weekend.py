import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Fix path to import from ml/
_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from export_predictions import RACES_2026

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
