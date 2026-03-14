"""Download Ergast F1 historical data (CSV)."""
import sys
import zipfile
from pathlib import Path
import requests

# Allow running from project root or from ml/
_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))
from config import RAW_DIR, ERGAST_CSV_URL, ERGAST_ZIP_PATH


def download_ergast_csv(force: bool = False) -> Path:
    """Download f1db_csv.zip from Ergast and extract to RAW_DIR."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if ERGAST_ZIP_PATH.exists() and not force:
        print(f"Already exists: {ERGAST_ZIP_PATH}")
        _extract(ERGAST_ZIP_PATH)
        return ERGAST_ZIP_PATH
    print(f"Downloading {ERGAST_CSV_URL} ...")
    r = requests.get(ERGAST_CSV_URL, timeout=60)
    r.raise_for_status()
    ERGAST_ZIP_PATH.write_bytes(r.content)
    print(f"Saved to {ERGAST_ZIP_PATH}")
    _extract(ERGAST_ZIP_PATH)
    return ERGAST_ZIP_PATH


def _extract(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(RAW_DIR)
    print(f"Extracted to {RAW_DIR}")


if __name__ == "__main__":
    download_ergast_csv()
