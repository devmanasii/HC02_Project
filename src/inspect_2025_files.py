
from pathlib import Path
import pandas as pd

folder = Path("data/original/nhs_2025")

files = sorted(folder.glob("*.csv"))

print("Number of CSV files found:", len(files))

for file in files:
    print("\n" + "=" * 50)
    print("File:", file.name)

    try:
        df = pd.read_csv(file, low_memory=False)

        print("Rows:", len(df))
        print("Columns:", len(df.columns))
        print("Column names:")
        print(df.columns.tolist())

        print("\nFirst 3 rows:")
        print(df.head(3).to_string(index=False))

    except Exception as error:
        print("Could not read this file:", error)