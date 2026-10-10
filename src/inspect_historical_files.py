
import pandas as pd
from pathlib import Path

files = [
    Path("data/original/nhs_historical/2023/April-2023-revised-130624-defv1.csv"),
    Path("data/original/nhs_historical/2024/Monthly-AE-April-2024-revised.csv"),
    Path("data/original/nhs_2025/May-2025-CSV-revised.csv"),
]

for file in files:
    print("\n" + "=" * 70)
    print("FILE:", file.name)

    if not file.exists():
        print("ERROR: File not found:", file)
        continue

    data = pd.read_csv(file, nrows=3)

    print("\nCOLUMNS:")
    for column in data.columns:
        print("-", repr(column))

    print("\nFIRST TWO ROWS:")
    print(data.head(2).to_string(index=False))