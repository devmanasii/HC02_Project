
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"

attendance_file = DATA_DIR / "heat_model_data_verified.csv"
weather_file = DATA_DIR / "monthly_weather_rebuilt.csv"
output_file = DATA_DIR / "heat_model_data_rebuilt.csv"

attendance = pd.read_csv(attendance_file)
weather = pd.read_csv(weather_file)

attendance["Month"] = pd.to_datetime(
    attendance["Month"]
).dt.to_period("M").astype(str)

weather["Month"] = pd.to_datetime(
    weather["Month"]
).dt.to_period("M").astype(str)

merged = attendance.drop(
    columns=[
        "Avg_Max_Temp_C",
        "Avg_Min_Temp_C",
        "Highest_Temp_C",
        "Avg_Humidity_Pct",
        "Hot_Days",
    ],
    errors="ignore",
).merge(
    weather,
    on="Month",
    how="inner",
    validate="one_to_one",
)

merged = merged.sort_values("Month").reset_index(drop=True)

print("Merged monthly records:", len(merged))
print("Date range:", merged["Month"].min(), "to", merged["Month"].max())
print("\nFirst 5 records:")
print(merged.head().to_string(index=False))

if merged.empty:
    raise ValueError("No matching months were found.")

if merged.isna().any().any():
    raise ValueError("Missing values found. Check the source data.")

merged.to_csv(output_file, index=False)
print("\nSaved:", output_file)