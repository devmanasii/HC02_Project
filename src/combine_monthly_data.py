
from pathlib import Path
import pandas as pd

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "original" / "nhs_monthly"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "nhs_monthly_combined.csv"

# Find all CSV files
csv_files = sorted(INPUT_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in: {INPUT_DIR}\n"
        "Place your downloaded CSV files in this folder."
    )

dataframes = []

for file_path in csv_files:
    print(f"\nReading: {file_path.name}")

    df = pd.read_csv(file_path, low_memory=False)

    # Normalize column names for comparison
    df.columns = (
        df.columns.astype(str)
        .str.strip()
    )

    print("Rows:", len(df))
    print("Columns:", list(df.columns))

    # Preserve the source filename for traceability
    df["Source_File"] = file_path.name

    dataframes.append(df)

# Combine files; columns that differ between files are retained
combined = pd.concat(
    dataframes,
    ignore_index=True,
    sort=False
)

print("\n--- Combined dataset ---")
print("Number of files:", len(csv_files))
print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))

# Save combined data
combined.to_csv(OUTPUT_FILE, index=False)

print("\nCombined file saved to:")
print(OUTPUT_FILE)

print("\nFirst five rows:")
print(combined.head().to_string(index=False))