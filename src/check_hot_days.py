
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "processed" / "monthly_weather.csv"

df = pd.read_csv(FILE)

print("Columns:", df.columns.tolist())
print("\nFirst 10 weather records:")
print(df.head(10).to_string(index=False))

print("\nHot_Days summary:")
if "Hot_Days" in df.columns:
    print(df["Hot_Days"].describe())
    print("\nDistinct Hot_Days values:")
    print(sorted(df["Hot_Days"].dropna().unique().tolist()))
else:
    print("Hot_Days is not present in this file.")