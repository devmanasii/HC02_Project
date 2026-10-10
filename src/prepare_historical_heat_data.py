
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

attendance_file = (
    DATA_DIR / "nhs_monthly_attendance_2023_2024.csv"
)
weather_file = (
    DATA_DIR / "monthly_weather_2023_2024.csv"
)
output_file = (
    DATA_DIR / "heat_model_data_2023_2024.csv"
)

attendance = pd.read_csv(attendance_file)
weather = pd.read_csv(weather_file)

# Ensure month values use the same format.
attendance["Month"] = attendance["Month"].astype(str)
weather["Month"] = weather["Month"].astype(str)

combined = pd.merge(
    attendance,
    weather,
    on="Month",
    how="inner",
    validate="one_to_one",
)

combined = combined.sort_values("Month")

combined.to_csv(output_file, index=False)

print("Historical heat dataset created.")
print("Rows:", len(combined))
print("Columns:", list(combined.columns))
print("Missing values:")
print(combined.isnull().sum())
print("\nFirst five rows:")
print(combined.head().to_string(index=False))
print("\nLast five rows:")
print(combined.tail().to_string(index=False))
print("\nSaved to:", output_file)