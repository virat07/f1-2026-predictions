import os
import argparse
import fastf1
from datetime import datetime
from supabase import create_client, Client

# --- Configuration ---
URL = os.getenv("SUPABASE_URL") or "https://eiczartjsujqyxqgaufg.supabase.co"
KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVpY3phcnRqc3VqcXl4cWdhdWZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1MjQ1MzgsImV4cCI6MjA4OTEwMDUzOH0.bCP4PU-MjvnX-1XiZMMbWWaOaGrFRoCtF5sWULdLZds"

supabase: Client = create_client(URL, KEY)

def sync_all_results(year=2026):
    """Iterate across all rounds and sync available data from FastF1 to Supabase."""
    print(f"🏎️ Scanning {year} season for new data via FastF1...")
    
    # Optional: Enable caching for FastF1 to speed up repeated runs
    cache_path = os.path.join("ml", "processed", "fastf1_cache")
    if os.path.exists(cache_path):
        fastf1.Cache.enable_cache(cache_path)

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    
    for _, event in schedule.iterrows():
        round_id = event['RoundNumber']
        if round_id == 0: continue
        
        entry = {"round": round_id}
        has_new_data = False

        # 1. Try to fetch Qualifying (Pole Winner)
        try:
            q_session = fastf1.get_session(year, round_id, 'Q')
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
            r_session = fastf1.get_session(year, round_id, 'R')
            r_session.load(laps=False, telemetry=False, weather=False, messages=False)
            if not r_session.results.empty:
                race_winner = r_session.results.iloc[0]
                entry["race_winner"] = race_winner['FullName']
                entry["team_winner"] = race_winner['TeamName']
                has_new_data = True
        except Exception:
            pass

        if has_new_data:
            print(f"📡 [SYNC] Round {round_id}: {entry.get('qualy_winner', 'N/A')} (Pole) | {entry.get('race_winner', 'N/A')} (Winner)")
            supabase.table("actual_results").upsert(entry, on_conflict="round").execute()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=2026, help="Season to sync")
    args = parser.parse_args()
    
    sync_all_results(args.year)
    print("✅ Full sync complete.")

if __name__ == "__main__":
    main()
