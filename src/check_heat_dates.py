
import pandas as pd
from pathlib import Path

folder = Path("data/processed")

files = [
    "balanced_monthly_attendance.csv",
    "heat_model_predictions.csv",
]

for filename in files:
    path = folder / filename

    print(f"\n{'=' * 50}")
    print("FILE:", filename)

    df = pd.read_csv(path)

    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    if "Month" in df.columns:
        print("\nOriginal Month values:")
        print(df["Month"].head(5).tolist())

        parsed = pd.to_datetime(df["Month"], errors="coerce")

        print("\nParsed Month values:")
        print(parsed.head(5).tolist())
        print("Valid dates:", parsed.notna().sum())
        print("Missing/invalid dates:", parsed.isna().sum())

