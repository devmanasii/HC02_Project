
import pandas as pd
from pathlib import Path

# Input files
nhs_file = Path("data/processed/nhs_2025_target.csv")
weather_file = Path("data/processed/monthly_weather.csv")

# Output file
output_file = Path("data/processed/nhs_weather_2025.csv")

# Read datasets
nhs = pd.read_csv(nhs_file)
weather = pd.read_csv(weather_file)

# Ensure Month columns use the same datetime format
nhs["Month"] = pd.to_datetime(nhs["Month"], errors="coerce")
weather["Month"] = pd.to_datetime(weather["Month"], errors="coerce")

# Keep only weather months that overlap with NHS 2025 data
weather_2025 = weather[
    weather["Month"].dt.year == 2025
].copy()

# Merge attendance with monthly weather
merged = nhs.merge(
    weather_2025,
    on="Month",
    how="left",
    validate="many_to_one"
)

# Check the merge
weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

print("NHS rows:", len(nhs))
print("Merged rows:", len(merged))
print("Unique months:", merged["Month"].nunique())
print("\nMissing values in weather columns:")
print(merged[weather_columns].isnull().sum())

# Save merged dataset
output_file.parent.mkdir(parents=True, exist_ok=True)
merged.to_csv(output_file, index=False)

print("\nMerged dataset saved to:", output_file)
print("\nFirst 5 rows:")
print(
    merged[
        [
            "Month",
            "Org Code",
            "Org name",
            "Total_AE_Attendances",
            "Avg_Max_Temp_C",
            "Highest_Temp_C",
            "Hot_Days",
        ]
    ].head().to_string(index=False)
)
id="m4n8zs"

