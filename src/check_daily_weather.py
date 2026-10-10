
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "processed" / "weather_cleaned.csv"

df = pd.read_csv(FILE)

print("Columns:", df.columns.tolist())
print("\nShape:", df.shape)
print("\nFirst five rows:")
print(df.head().to_string(index=False))