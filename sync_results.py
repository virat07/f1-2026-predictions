import os
import argparse
import fastf1
from datetime import datetime
from supabase import create_client, Client

# --- Configuration ---
URL = os.getenv("SUPABASE_URL") or "https://eiczartjsujqyxqgaufg.supabase.co"
KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpY3phcnRqc3VqcXl4cWdhdWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MjQ1MzgsImV4cCI6MjA4OTEwMDUzOH0.bCP4PU-MjvnX-1XiZMMbWWaOaGrFRoCtF5sWULdLZds"

# Map FastF1 EventName to the frontend round number (from f1Data.js)
FASTF1_TO_FRONTEND_ROUND = {
    "Australian Grand Prix": 1,
    "Chinese Grand Prix": 2,
    "Japanese Grand Prix": 3,
    "Miami Grand Prix": 6,
    "Canadian Grand Prix": 7,
    "Monaco Grand Prix": 8,
    "Barcelona Grand Prix": 9,      # Spanish Grand Prix (Barcelona) in f1Data.js
    "Austrian Grand Prix": 10,
    "British Grand Prix": 11,
    "Belgian Grand Prix": 12,
    "Hungarian Grand Prix": 13,
    "Dutch Grand Prix": 14,
    "Italian Grand Prix": 15,
    "Spanish Grand Prix": 16,        # Madrid Grand Prix in f1Data.js
    "Azerbaijan Grand Prix": 17,
    "Singapore Grand Prix": 18,
    "United States Grand Prix": 19,
    "Mexico City Grand Prix": 20,    # Mexican Grand Prix
    "São Paulo Grand Prix": 21,      # Brazilian Grand Prix
    "Las Vegas Grand Prix": 22,
    "Qatar Grand Prix": 23,
    "Abu Dhabi Grand Prix": 24,
}

supabase: Client = create_client(URL, KEY)

def sync_all_results(year=2026):
    """Iterate across all rounds and sync available data from FastF1 to Supabase."""
    print(f"🏎️ Scanning {year} season for new data via FastF1...")
    
    # Optional: Enable caching for FastF1 to speed up repeated runs
    cache_path = os.path.join("ml", "processed", "fastf1_cache")
    if os.path.exists(cache_path):
        fastf1.Cache.enable_cache(cache_path)

    # Clear legacy incorrect rounds (Bahrain/Sakhir round 4, Saudi Arabia/Jeddah round 5)
    # which do not exist in the official 2026 schedule but were populated due to round mismatches
    for r in [4, 5]:
        try:
            supabase.table("actual_results").delete().eq("round", r).execute()
            print(f"🗑️ Cleared legacy incorrect results for Round {r} (Bahrain/Saudi)")
        except Exception as e:
            print(f"⚠️ Failed to clear Round {r}: {e}")

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    
    for _, event in schedule.iterrows():
        event_name = event['EventName']
        round_num = event['RoundNumber']
        round_id = FASTF1_TO_FRONTEND_ROUND.get(event_name)
        if round_id is None:
            if round_num != 0:
                print(f"⚠️ Skipping unknown FastF1 event: {event_name}")
            continue
        
        entry = {"round": round_id}
        has_new_data = False

        # 1. Try to fetch Qualifying (Pole Winner)
        try:
            q_session = fastf1.get_session(year, round_num, 'Q')
            q_session.load(laps=False, telemetry=False, weather=False, messages=False)
            if not q_session.results.empty:
                pole_winner = q_session.results.iloc[0]
                entry["qualy_winner"] = pole_winner['FullName']
                entry["team_winner"] = pole_winner['TeamName'] # Assumption: use pole team as interim
                has_new_data = True
        except Exception:
            pass # Session results not yet available

        # 2. Try to fetch Race (Race Winner)
        try:
            r_session = fastf1.get_session(year, round_num, 'R')
            r_session.load(laps=False, telemetry=False, weather=False, messages=False)
            if not r_session.results.empty:
                race_winner = r_session.results.iloc[0]
                entry["race_winner"] = race_winner['FullName']
                entry["team_winner"] = race_winner['TeamName']
                has_new_data = True
        except Exception:
            pass

        if has_new_data:
            print(f"📡 [SYNC] Round {round_id} ({event_name}): {entry.get('qualy_winner', 'N/A')} (Pole) | {entry.get('race_winner', 'N/A')} (Winner)")
            supabase.table("actual_results").upsert(entry, on_conflict="round").execute()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2026, help="Season to sync")
    args = parser.parse_args()
    
    sync_all_results(args.year)
    print("✅ Full sync complete.")

if __name__ == "__main__":
    main()
