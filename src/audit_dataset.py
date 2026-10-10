
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
file = root / "data" / "processed" / "heat_model_data_2023_2026.csv"

df = pd.read_csv(file)
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")

print("\nDATASET OVERVIEW")
print("Rows:", len(df))
print("Date range:", df["Month"].min(), "to", df["Month"].max())
print("Duplicate months:", df["Month"].duplicated().sum())

print("\nMISSING VALUES")
print(df.isnull().sum().to_string())

print("\nDATA TYPES")
print(df.dtypes.to_string())

print("\nNUMERIC SUMMARY")
print(df.select_dtypes(include="number").describe().round(2).to_string())

print("\nMONTHLY ATTENDANCE AND WEATHER")
print(df.to_string(index=False))

weather_file = root / "data" / "processed" / "monthly_weather.csv"

if weather_file.exists():
    weather = pd.read_csv(weather_file)
    print("\nWEATHER DATA OVERVIEW")
    print("Rows:", len(weather))
    print("Columns:", weather.columns.tolist())
    print(weather.head().to_string(index=False))