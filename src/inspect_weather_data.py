
import pandas as pd
from pathlib import Path

file_path = Path(
    "data/original/weather/historical_weather.csv"
)

# The actual column headings start on line 2 of the displayed data
df = pd.read_csv(file_path, skiprows=2)

# Remove accidental spaces from column names
df.columns = df.columns.str.strip()

print("WEATHER DATA LOADED SUCCESSFULLY")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nFIRST 10 ROWS:")
print(df.head(10).to_string(index=False))

print("\nMISSING VALUES:")
print(df.isna().sum().to_string())

print("\nDATA TYPES:")
print(df.dtypes.to_string())