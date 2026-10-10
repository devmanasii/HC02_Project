
import pandas as pd
from pathlib import Path

attendance_file = Path("data/processed/balanced_monthly_attendance.csv")
weather_file = Path("data/processed/monthly_weather.csv")
output_file = Path("data/processed/heat_model_data.csv")

# Load hospital attendance
attendance = pd.read_csv(attendance_file)
attendance["Month"] = pd.to_datetime(attendance["Month"])

# Load monthly weather
weather = pd.read_csv(weather_file)
weather["Month"] = pd.to_datetime(weather["Month"])

# Combine using the month
combined = attendance.merge(
    weather,
    on="Month",
    how="left"
)

# Save combined dataset
combined.to_csv(output_file, index=False)

print("Combined dataset created successfully!")
print("Rows:", len(combined))
print("Columns:", combined.columns.tolist())
print("\nDate range:")
print("First month:", combined["Month"].min().strftime("%Y-%m"))
print("Last month:", combined["Month"].max().strftime("%Y-%m"))

print("\nMissing values:")
print(combined.isna().sum())

print("\nLatest 8 months:")
print(combined.tail(8).to_string(index=False))

print("\nSaved:", output_file)