
from pathlib import Path
import pandas as pd

input_folder = Path("data/original/nhs_2025")
output_file = Path("data/processed/nhs_2025_combined.csv")

files = sorted(input_folder.glob("*.csv"))

if len(files) != 12:
    raise ValueError(
        f"Expected 12 monthly CSV files, but found {len(files)}."
    )

dataframes = []

for file in files:
    print("Reading:", file.name)

    df = pd.read_csv(file, low_memory=False)

    # Remove accidental spaces from column names.
    df.columns = df.columns.str.strip()

    # Record the original filename for traceability.
    df["Source_File"] = file.name

    dataframes.append(df)

combined = pd.concat(dataframes, ignore_index=True, sort=False)

output_file.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(output_file, index=False)

print("\nCOMBINATION COMPLETE")
print("Files combined:", len(files))
print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))
print("Output saved to:", output_file)

print("\nRows per reporting period:")
print(combined["Period"].value_counts().sort_index().to_string())

print("\nFirst 5 rows:")
print(combined.head().to_string(index=False))