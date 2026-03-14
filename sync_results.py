import argparse
import time
from datetime import datetime
from supabase import create_client, Client

# Configuration
URL = "https://eiczartjsujqyxqgaufg.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpY3phcnRqc3VqcXl4cWdhdWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MjQ1MzgsImV4cCI6MjA4OTEwMDUzOH0.bCP4PU-MjvnX-1XiZMMbWWaOaGrFRoCtF5sWULdLZds"

supabase: Client = create_client(URL, KEY)

# Pre-defined results for automation (Mocking the 2026 season flow)
SEASON_RESULTS = {
    1: {"race_winner": "George Russell", "qualy_winner": "George Russell", "team_winner": "Mercedes-AMG Petronas"},
    2: {"race_winner": "Lando Norris", "qualy_winner": "Lando Norris", "sprint_winner": "Charles Leclerc", "team_winner": "McLaren F1 Team"},
}

def publish_result(round_id):
    if round_id in SEASON_RESULTS:
        data = SEASON_RESULTS[round_id]
        data["round"] = round_id
        print(f"📡 [AUTO] Publishing results for Round {round_id}...")
        supabase.table("actual_results").upsert(data, on_conflict="round").execute()
        print(f"✅ Round {round_id} is now OFFICIAL.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true', help="Keep script running and publish based on time")
    args = parser.parse_args()

    if not args.watch:
        # Manual one-time sync for current round
        publish_result(1)
        return

    print("🕵️ F1 RACE CONTROL: WATCH MODE ACTIVE")
    print("Monitoring 2026 Schedule...")
    
    while True:
        now = datetime.now()
        # Logic: If current time > Race End Time, publish result
        # Example: Chinese GP ends Mar 15, 2026
        if now >= datetime(2026, 3, 15, 10, 0) and now < datetime(2026, 3, 15, 10, 5):
            publish_result(2)
        
        time.sleep(300) # Check every 5 minutes

if __name__ == "__main__":
    main()
