
import pandas as pd
from pathlib import Path

# Input and output files
input_file = Path("data/processed/weather_cleaned.csv")
output_file = Path("data/processed/monthly_weather.csv")

# Read cleaned daily weather data
df = pd.read_csv(input_file)

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Remove rows with invalid dates
df = df.dropna(subset=["date"])

# Create a monthly date column
df["Month"] = df["date"].dt.to_period("M").dt.to_timestamp()

# Summarize daily weather into monthly features
monthly_weather = (
    df.groupby("Month")
    .agg(
        Avg_Max_Temp_C=("max_temp_c", "mean"),
        Avg_Min_Temp_C=("min_temp_c", "mean"),
        Highest_Temp_C=("max_temp_c", "max"),
        Avg_Humidity_Pct=("humidity_pct", "mean"),
        Hot_Days=("max_temp_c", lambda x: (x >= 30).sum()),
    )
    .reset_index()
)

# Round weather values for readability
weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
]

monthly_weather[weather_columns] = (
    monthly_weather[weather_columns].round(2)
)

# Save monthly weather data
output_file.parent.mkdir(parents=True, exist_ok=True)
monthly_weather.to_csv(output_file, index=False)

print("Monthly weather data created successfully!")
print("Number of months:", len(monthly_weather))
print("Missing values:")
print(monthly_weather.isnull().sum())
print("\nFirst 5 rows:")
print(monthly_weather.head().to_string(index=False))
print("\nSaved to:", output_file)

