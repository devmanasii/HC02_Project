
import pandas as pd
from pathlib import Path

# File paths
input_file = Path("data/original/weather/historical_weather.csv")
output_file = Path("data/processed/weather_cleaned.csv")

# Read weather CSV, skipping the metadata rows
df = pd.read_csv(input_file, skiprows=2)
df.columns = df.columns.str.strip()

# Rename columns to simple names
df = df.rename(columns={
    "time": "date",
    "temperature_2m_max (°C)": "max_temp_c",
    "temperature_2m_min (°C)": "min_temp_c",
    "relative_humidity_2m_mean (%)": "humidity_pct"
})

# Convert date to proper date format
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Ensure weather measurements are numeric
weather_columns = ["max_temp_c", "min_temp_c", "humidity_pct"]

for column in weather_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Sort by date
df = df.sort_values("date").reset_index(drop=True)

# Check data quality
print("Rows before cleaning:", len(df))

df = df.dropna(
    subset=["date", "max_temp_c", "min_temp_c", "humidity_pct"]
)

print("Rows after removing missing values:", len(df))
print("Duplicate dates:", df["date"].duplicated().sum())

# Save cleaned data
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\nCleaned weather dataset saved to:", output_file)
print("\nFirst 5 rows:")
print(df.head().to_string(index=False))

print("\nDate range:")
print(df["date"].min(), "to", df["date"].max())