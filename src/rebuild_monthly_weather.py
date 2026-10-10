
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"

daily_file = DATA_DIR / "weather_cleaned.csv"
output_file = DATA_DIR / "monthly_weather_rebuilt.csv"

df = pd.read_csv(daily_file)
df["date"] = pd.to_datetime(df["date"], errors="coerce")

df["max_temp_c"] = pd.to_numeric(df["max_temp_c"], errors="coerce")
df["min_temp_c"] = pd.to_numeric(df["min_temp_c"], errors="coerce")
df["humidity_pct"] = pd.to_numeric(df["humidity_pct"], errors="coerce")

df = df.dropna(
    subset=["date", "max_temp_c", "min_temp_c", "humidity_pct"]
).copy()

# Provisional project threshold: a hot day has maximum temperature >= 30°C
HOT_DAY_THRESHOLD_C = 30

df["Month"] = df["date"].dt.to_period("M")

monthly = df.groupby("Month").agg(
    Avg_Max_Temp_C=("max_temp_c", "mean"),
    Avg_Min_Temp_C=("min_temp_c", "mean"),
    Highest_Temp_C=("max_temp_c", "max"),
    Avg_Humidity_Pct=("humidity_pct", "mean"),
    Hot_Days=("max_temp_c", lambda x: int((x >= HOT_DAY_THRESHOLD_C).sum())),
    Days_With_Data=("date", "count"),
).reset_index()

monthly["Month"] = monthly["Month"].astype(str)

monthly.to_csv(output_file, index=False)

print("Daily records used:", len(df))
print("Monthly records created:", len(monthly))
print("Hot-day threshold:", HOT_DAY_THRESHOLD_C, "°C")
print("\nFirst 10 months:")
print(monthly.head(10).to_string(index=False))

print("\nMonths with most hot days:")
print(
    monthly.sort_values("Hot_Days", ascending=False)
    .head(5)[["Month", "Highest_Temp_C", "Hot_Days", "Days_With_Data"]]
    .to_string(index=False)
)

print("\nSaved:", output_file)