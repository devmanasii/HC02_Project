
import pandas as pd
from pathlib import Path

# Load merged dataset
input_file = Path("data/processed/nhs_weather_2025.csv")
df = pd.read_csv(input_file)

df["Month"] = pd.to_datetime(df["Month"])

# 1. Summarize attendance by month
monthly_attendance = (
    df.groupby("Month")["Total_AE_Attendances"]
    .sum()
    .reset_index()
)

# 2. Get one weather record per month
monthly_weather = (
    df.groupby("Month")
    .agg(
        Avg_Max_Temp_C=("Avg_Max_Temp_C", "first"),
        Highest_Temp_C=("Highest_Temp_C", "first"),
        Hot_Days=("Hot_Days", "first"),
        Avg_Humidity_Pct=("Avg_Humidity_Pct", "first"),
    )
    .reset_index()
)

# 3. Combine monthly summaries
monthly_analysis = monthly_attendance.merge(
    monthly_weather,
    on="Month",
    how="inner",
    validate="one_to_one"
)

# 4. Display results
print("\nMONTHLY A&E ATTENDANCE AND WEATHER")
print(monthly_analysis.to_string(index=False))

print("\nHIGHEST ATTENDANCE MONTH")
print(
    monthly_analysis.loc[
        monthly_analysis["Total_AE_Attendances"].idxmax()
    ].to_string()
)

print("\nHOTTEST MONTH BY AVERAGE MAXIMUM TEMPERATURE")
print(
    monthly_analysis.loc[
        monthly_analysis["Avg_Max_Temp_C"].idxmax()
    ].to_string()
)

# 5. Calculate correlation
correlation = monthly_analysis[
    ["Total_AE_Attendances", "Avg_Max_Temp_C", "Highest_Temp_C", "Hot_Days"]
].corr()

print("\nCORRELATION MATRIX")
print(correlation.round(3).to_string())

# 6. Save monthly analysis
output_file = Path("data/processed/monthly_analysis_2025.csv")
monthly_analysis.to_csv(output_file, index=False)

print("\nMonthly analysis saved to:", output_file)
id="j5s2tw"

