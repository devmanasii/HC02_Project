
import pandas as pd
from pathlib import Path

# Load the existing monthly weather data (2024–2025)
old_file = Path("data/processed/monthly_weather.csv")
old_weather = pd.read_csv(old_file)
old_weather["Month"] = pd.to_datetime(old_weather["Month"])

# Load the newly downloaded daily weather data for 2026
new_file = Path("data/original/weather/weather_2026_daily.csv")
daily = pd.read_csv(new_file)
daily["Date"] = pd.to_datetime(daily["Date"])

# Convert daily weather into monthly summaries
daily["Month"] = daily["Date"].dt.to_period("M").dt.to_timestamp()

monthly_2026 = daily.groupby("Month").agg(
    Avg_Max_Temp_C=("Max_Temp_C", "mean"),
    Avg_Min_Temp_C=("Min_Temp_C", "mean"),
    Highest_Temp_C=("Max_Temp_C", "max"),
    Avg_Humidity_Pct=("Humidity_Pct", "mean"),
    Hot_Days=("Max_Temp_C", lambda x: (x >= 30).sum())
).reset_index()

# Combine old and new weather data
combined = pd.concat(
    [old_weather, monthly_2026],
    ignore_index=True
)

combined = combined.drop_duplicates(subset=["Month"], keep="last")
combined = combined.sort_values("Month").reset_index(drop=True)

# Save the extended weather dataset
output_file = Path("data/processed/monthly_weather.csv")
combined.to_csv(output_file, index=False)

print("Total monthly rows:", len(combined))
print("First month:", combined["Month"].min().strftime("%Y-%m"))
print("Last month:", combined["Month"].max().strftime("%Y-%m"))
print("\n2026 monthly weather:")
print(combined[combined["Month"].dt.year == 2026].to_string(index=False))
print("\nMissing values:")
print(combined.isna().sum())
print("\nSaved:", output_file)