"""Load seasonal CSV and return merged DataFrames for modeling, falling back to local files."""
import sys
import glob
from pathlib import Path
import pandas as pd
import numpy as np

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))
from config import RAW_DIR, MIN_SEASON, MAX_SEASON

def _standardize_team_name(name):
    if not isinstance(name, str): return name
    n = name.lower()
    
    # Prioritize Brand Name over Engine Name
    if 'red bull' in n: return 'Red Bull Racing'
    if 'mercedes' in n and 'mercedes-amg' not in n and n.startswith('mercedes'): return 'Mercedes'
    if 'mercedes' in n and n.startswith('mercedes'): return 'Mercedes'
    
    if 'ferrari' in n:
        if 'haas' in n: return 'Haas F1 Team'
        if 'cadillac' in n: return 'Cadillac'
        return 'Ferrari'
    
    if 'mclaren' in n: return 'McLaren'
    if 'aston martin' in n: return 'Aston Martin'
    if 'alpine' in n: return 'Alpine'
    if 'williams' in n: return 'Williams'
    if 'haas' in n: return 'Haas F1 Team'
    if 'racing bulls' in n or (n.startswith('rb ') and 'honda' in n) or n == 'rb': return 'Racing Bulls'
    if 'audi' in n or 'sauber' in n or 'alfa romeo' in n: return 'Audi'
    if 'cadillac' in n or 'andretti' in n: return 'Cadillac'
    
    # Catch-all for Mercedes if not caught above
    if 'mercedes' in n:
        if 'mclaren' in n: return 'McLaren'
        if 'williams' in n: return 'Williams'
        if 'alpine' in n: return 'Alpine'
        return 'Mercedes'
        
    return name

def _ergast_files_present() -> bool:
    return (RAW_DIR / "results.csv").exists() and (RAW_DIR / "races.csv").exists()


def _load_ergast_tables():
    results_path = RAW_DIR / "results.csv"
    races_path = RAW_DIR / "races.csv"
    drivers_path = RAW_DIR / "drivers.csv"
    constructors_path = RAW_DIR / "constructors.csv"
    circuits_path = RAW_DIR / "circuits.csv"
    if not results_path.exists() or not races_path.exists():
        return None
    results = pd.read_csv(results_path)
    races = pd.read_csv(races_path)
    drivers = pd.read_csv(drivers_path) if drivers_path.exists() else pd.DataFrame()
    constructors = pd.read_csv(constructors_path) if constructors_path.exists() else pd.DataFrame()
    circuits = pd.read_csv(circuits_path) if circuits_path.exists() else pd.DataFrame()
    return results, races, drivers, constructors, circuits


def _load_ergast_data(season_min: int, season_max: int) -> pd.DataFrame:
    tables = _load_ergast_tables()
    if tables is None:
        return pd.DataFrame()
    results, races, drivers, constructors, circuits = tables
    races = races[(races["year"] >= season_min) & (races["year"] <= season_max)]
    if races.empty or results.empty:
        return pd.DataFrame()
    merged = results.merge(races, on="raceId", how="inner", suffixes=("", "_race"))
    if not constructors.empty:
        merged = merged.merge(constructors, on="constructorId", how="left", suffixes=("", "_ctor"))
    if not drivers.empty:
        merged = merged.merge(drivers, on="driverId", how="left", suffixes=("", "_drv"))
    if not circuits.empty:
        merged = merged.merge(circuits, on="circuitId", how="left", suffixes=("", "_circuit"))
    forename = merged["forename"] if "forename" in merged.columns else pd.Series("", index=merged.index)
    surname = merged["surname"] if "surname" in merged.columns else pd.Series("", index=merged.index)
    merged["driver_name"] = (forename + " " + surname).str.strip()
    if "name_ctor" in merged.columns:
        ctor_name = merged["name_ctor"]
    else:
        ctor_name = pd.Series("", index=merged.index)
    merged["constructor_name"] = ctor_name.astype(str)
    merged["constructor_name"] = merged["constructor_name"].apply(_standardize_team_name)
    merged["race_name"] = merged["name"] if "name" in merged.columns else pd.Series("", index=merged.index)
    merged["positionOrder"] = pd.to_numeric(merged.get("positionOrder", merged.get("position", 0)), errors="coerce").fillna(0).astype(int)
    merged["grid"] = pd.to_numeric(merged.get("grid", 0), errors="coerce").fillna(20).astype(int)
    merged["points"] = pd.to_numeric(merged.get("points", 0), errors="coerce").fillna(0)
    merged["round"] = pd.to_numeric(merged.get("round", 0), errors="coerce").fillna(0).astype(int)
    if "driverRef" not in merged.columns:
        merged["driverRef"] = merged["driver_name"].str.lower().str.replace(" ", "_")
    if "constructorRef" not in merged.columns:
        merged["constructorRef"] = merged["constructor_name"].str.lower().str.replace(" ", "_")
    if "circuitRef" not in merged.columns:
        merged["circuitRef"] = merged["race_name"].str.lower().str.replace(" ", "_")
    if "forename" not in merged.columns:
        merged["forename"] = merged["driver_name"].str.split(" ").str[0].fillna("")
    if "surname" not in merged.columns:
        merged["surname"] = merged["driver_name"].str.split(" ").str[1].fillna("")
    return merged[
        [
            "raceId",
            "year",
            "round",
            "circuitId",
            "circuitRef",
            "race_name",
            "constructorId",
            "constructorRef",
            "constructor_name",
            "driverId",
            "driverRef",
            "driver_name",
            "forename",
            "surname",
            "positionOrder",
            "grid",
            "points",
        ]
    ]


def _load_custom_seasonal_data(season_min: int = 2018, season_max: int = 2026) -> pd.DataFrame:
    """Read all seasonal CSVs and merge into a single results DataFrame."""
    all_results = []
    for year in range(season_min, season_max + 1):
        pattern = f"*_{year}*[Ss]eason*raceResults.csv"
        files = list(RAW_DIR.glob(pattern))
        if not files:
            pattern = f"*_{year}*raceResults.csv"
            files = list(RAW_DIR.glob(pattern))
        if not files:
            continue
        df = pd.read_csv(files[0], on_bad_lines="skip")
        df["year"] = year
        column_map = {
            "Track": "race_name",
            "Position": "positionOrder",
            "Starting Grid": "grid",
            "Points": "points",
            "Driver": "driver_name",
            "Team": "constructor_name",
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        df["positionOrder"] = pd.to_numeric(df["positionOrder"], errors="coerce").fillna(20).astype(int)
        df["grid"] = pd.to_numeric(df["grid"], errors="coerce").fillna(20).astype(int)
        df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
        df["constructor_name"] = df["constructor_name"].apply(_standardize_team_name)
        all_results.append(df)
    if not all_results:
        return pd.DataFrame()
    combined = pd.concat(all_results, ignore_index=True)
    uq_drivers = sorted(combined["driver_name"].dropna().unique())
    driver_map = {name: i + 1 for i, name in enumerate(uq_drivers)}
    combined["driverId"] = combined["driver_name"].map(driver_map)
    combined["driverRef"] = combined["driver_name"].str.lower().str.replace(" ", "_")
    uq_team = sorted(combined["constructor_name"].dropna().unique())
    team_map = {name: i + 1 for i, name in enumerate(uq_team)}
    combined["constructorId"] = combined["constructor_name"].map(team_map)
    combined["constructorRef"] = combined["constructor_name"].str.lower().str.replace(" ", "_")
    uq_races = sorted(combined["race_name"].dropna().unique())
    race_map = {name: i + 1 for i, name in enumerate(uq_races)}
    combined["circuitId"] = combined["race_name"].map(race_map)
    combined["circuitRef"] = combined["race_name"].str.lower().str.replace(" ", "_")
    combined["raceId"] = (combined["year"].astype(str) + "_" + combined["race_name"]).factorize()[0] + 1
    if "Round" not in combined.columns:
        combined["round"] = combined.groupby("year").cumcount() // 20 + 1
    else:
        combined["round"] = combined["Round"]
    combined["forename"] = combined["driver_name"].apply(lambda x: x.split(" ")[0] if isinstance(x, str) else "")
    combined["surname"] = combined["driver_name"].apply(lambda x: x.split(" ")[1] if isinstance(x, str) and " " in x else "")
    return combined


def load_seasonal_data(season_min: int = 2018, season_max: int = 2026) -> pd.DataFrame:
    """Load Ergast CSVs when present, otherwise fall back to custom seasonal files."""
    if _ergast_files_present():
        ergast = _load_ergast_data(season_min, season_max)
        if not ergast.empty:
            return ergast
    return _load_custom_seasonal_data(season_min, season_max)

def build_race_results(season_min: int = MIN_SEASON, season_max: int = MAX_SEASON) -> pd.DataFrame:
    return load_seasonal_data(season_min, season_max)

def build_standings_tables(season_min: int = MIN_SEASON, season_max: int = MAX_SEASON):
    df = build_race_results(season_min, season_max)
    if df.empty: return None, None
    ds = df.groupby(['year', 'driverId', 'driver_name', 'driverRef', 'forename', 'surname']).agg({'points': 'sum'}).reset_index()
    cs = df.groupby(['year', 'constructorId', 'constructor_name', 'constructorRef']).agg({'points': 'sum'}).reset_index().rename(columns={'constructor_name': 'name'})
    return ds, cs

def load_drivers():
    df = load_seasonal_data()
    return df[['driverId', 'driver_name', 'driverRef', 'forename', 'surname']].drop_duplicates()

def load_constructors():
    df = load_seasonal_data()
    return df[['constructorId', 'constructor_name', 'constructorRef']].drop_duplicates().rename(columns={'constructor_name': 'name'})

def load_circuits():
    df = load_seasonal_data()
    return df[['circuitId', 'race_name', 'circuitRef']].rename(columns={'race_name': 'name'}).drop_duplicates()

def get_2026_teams():
    qual_file = RAW_DIR / "Formula1_2026Season_QualifyingResults.csv"
    if not qual_file.exists(): return []
    df = pd.read_csv(qual_file)
    return sorted(df['Team'].unique())

def get_standardized_name(name):
    return _standardize_team_name(name)

def get_2026_drivers():
    qual_file = RAW_DIR / "Formula1_2026Season_QualifyingResults.csv"
    race_file = RAW_DIR / "Formula1_2026Season_RaceResults.csv"
    d_names = set()
    for f in [qual_file, race_file]:
        if f.exists():
            df = pd.read_csv(f)
            d_names.update(df['Driver'].unique())
    return sorted(list(d_names))
