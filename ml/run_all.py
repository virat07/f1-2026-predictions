"""Download data, train models, and export predictions. Run from project root: python -m ml.run_all"""
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

def main():
    print("Step 1: Download data")
    from data.download_data import download_ergast_csv
    download_ergast_csv()
    print("\nStep 2: Train models")
    from train import main as train_main
    train_main()
    print("\nStep 3: Export predictions")
    from export_predictions import main as export_main
    export_main()
    print("\nAll done. Check ml/output/predictions.json")

if __name__ == "__main__":
    main()
