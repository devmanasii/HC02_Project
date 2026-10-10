
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "original" / "weather"
    / "weather_2023_2024_daily.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "monthly_weather_2023_2024.csv"
)

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly = (
    df.groupby("Month")
    .agg(
        Avg_Max_Temp_C=("Max_Temp_C", "mean"),
        Avg_Min_Temp_C=("Min_Temp_C", "mean"),
        Highest_Temp_C=("Max_Temp_C", "max"),
        Avg_Humidity_Pct=("Humidity_Pct", "mean"),
        Hot_Days=("Max_Temp_C", lambda x: (x >= 30).sum()),
    )
    .reset_index()
)

monthly = monthly.round(2)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
monthly.to_csv(OUTPUT_FILE, index=False)

print("Monthly weather processing complete.")
print("Number of months:", len(monthly))
print("Missing values:", monthly.isnull().sum().sum())
print("\nFirst five months:")
print(monthly.head().to_string(index=False))
print("\nLast five months:")
print(monthly.tail().to_string(index=False))
print("\nSaved to:", OUTPUT_FILE)