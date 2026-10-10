
import pandas as pd
from pathlib import Path

input_file = Path("data/processed/monthly_analysis_2025.csv")
output_file = Path("data/processed/forecasting_data_2025.csv")

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])

# Ensure one row per month
df = df.sort_values("Month").reset_index(drop=True)

# Check monthly records
print("Number of monthly records:", len(df))
print("Duplicate months:", int(df["Month"].duplicated().sum()))
print("Missing values:")
print(df.isnull().sum().to_string())

# Create previous-month attendance as a simple baseline
df["Previous_Month_Attendance"] = (
    df["Total_AE_Attendances"].shift(1)
)

# Save forecasting dataset
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\nForecasting dataset saved to:", output_file)
print("\nLast 5 rows:")
print(df.tail().to_string(index=False))

