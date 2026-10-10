
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
processed = root / "data" / "processed"

attendance_file = processed / "heat_model_data_balanced_2023_2026.csv"
weather_file = processed / "monthly_weather.csv"
output_file = processed / "heat_model_data_verified.csv"

# Load attendance and weather datasets
attendance = pd.read_csv(attendance_file)
weather = pd.read_csv(weather_file)

attendance["Month"] = pd.to_datetime(
    attendance["Month"], errors="coerce"
).dt.to_period("M").astype(str)

weather["Month"] = pd.to_datetime(
    weather["Month"], errors="coerce"
).dt.to_period("M").astype(str)

# Keep only the columns needed from each source
attendance = attendance[
    ["Month", "Total_AE_Attendances", "Provider_Count"]
]

weather_columns = [
    "Month",
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]
weather = weather[weather_columns]

# Use only months available in both datasets
verified = attendance.merge(
    weather,
    on="Month",
    how="inner",
    validate="one_to_one"
)

verified = verified.sort_values("Month").reset_index(drop=True)

# Check the data
print("Verified records:", len(verified))
print("Date range:", verified["Month"].min(), "to", verified["Month"].max())
print("Duplicate months:", verified["Month"].duplicated().sum())
print("Missing values:", int(verified.isna().sum().sum()))

print("\nProvider counts by month:")
print(verified[["Month", "Provider_Count"]].to_string(index=False))

print("\nFirst and last records:")
print(verified.head(3).to_string(index=False))
print(verified.tail(3).to_string(index=False))

if verified.empty:
    raise ValueError("No matching months found in attendance and weather data.")

if verified.isna().any().any():
    raise ValueError("Missing values found. Investigate before training.")

verified.to_csv(output_file, index=False)
print("\nSaved:", output_file)