import json
from pathlib import Path
import fastf1
import pandas as pd

CACHE_DIR = Path.home() / ".fastf1-cache"
fastf1.Cache.enable_cache(str(CACHE_DIR))

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_JSON = PROJECT_ROOT / "public" / "ml-predictions.json"

def main():
    if not PUBLIC_JSON.exists():
        print("ml-predictions.json not found")
        return
        
    data = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    
    # Track points
    driver_points = {}
    constructor_points = {}
    
    # Get actual results for 2026
    rnd = 1
    while True:
        try:
            session = fastf1.get_session(2026, rnd, "Race")
            session.load(telemetry=False, weather=False, messages=False)
            if session.results is None or session.results.empty:
                break
                
            for _, row in session.results.iterrows():
                driver = row['BroadcastName']
                team = row['TeamName']
                points = float(row.get('Points', 0) or 0)
                
                if driver not in driver_points:
                    driver_points[driver] = {'points': 0, 'team': team, 'number': row['DriverNumber']}
                driver_points[driver]['points'] += points
                
                if team not in constructor_points:
                    constructor_points[team] = 0
                constructor_points[team] += points
                
            rnd += 1
        except Exception as e:
            # Future race
            break
            
    # Add predicted points from ML race predictions
    for race in data.get("racePredictions", []):
        if race.get("round") >= rnd:
            predicted_team = race.get("predictedWinner")
            if predicted_team:
                if predicted_team not in constructor_points:
                    constructor_points[predicted_team] = 0
                constructor_points[predicted_team] += 25
                
                # Assign 25 points to the top driver of that team as a mock projection
                team_drivers = [d for d, info in driver_points.items() if info['team'] == predicted_team]
                if team_drivers:
                    top_driver = sorted(team_drivers, key=lambda x: driver_points[x]['points'], reverse=True)[0]
                    driver_points[top_driver]['points'] += 25

    # Format output for frontend JSON
    sorted_drivers = sorted(driver_points.items(), key=lambda x: x[1]['points'], reverse=True)
    sorted_constructors = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)
    
    podium = []
    rest = []
    
    for i, (driver, info) in enumerate(sorted_drivers):
        pos = i + 1
        driver_entry = {
            "name": driver,
            "number": info['number'],
            "team": info['team'],
            "points": info['points']
        }
        if pos <= 3:
            driver_entry["position"] = pos
            driver_entry["gradient"] = "linear-gradient(135deg, #ff6b35, #e8002d)"
            driver_entry["teamClass"] = "ml"
            driver_entry["note"] = "Projected based on ML race winner simulator & 2026 results."
            podium.append(driver_entry)
        else:
            driver_entry["pos"] = pos
            driver_entry["color"] = "#ffffff"
            rest.append(driver_entry)
            
    standings_ctors = []
    for i, (team, pts) in enumerate(sorted_constructors):
        standings_ctors.append({
            "rank": i + 1,
            "name": team,
            "points": pts,
            "color": "#e8002d",
            "note": "Projected from ML predictions & 2026 results."
        })
        
    data["driverStandings"] = {"podium": podium, "rest": rest}
    data["constructorStandings"] = standings_ctors
    
    PUBLIC_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Updated Championship Standings in ml-predictions.json!")

if __name__ == "__main__":
    main()
