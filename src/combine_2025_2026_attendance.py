
import pandas as pd
from pathlib import Path

# Input files
file_2025 = Path("data/processed/nhs_2025_target.csv")
file_2026 = Path("data/processed/nhs_monthly_target.csv")

# Output file
output_file = Path("data/processed/nhs_attendance_2025_2026.csv")

# Read both datasets
df_2025 = pd.read_csv(file_2025)
df_2026 = pd.read_csv(file_2026)

# Keep the required columns
columns = ["Month", "Org Code", "Total_AE_Attendances"]

df_2025 = df_2025[columns].copy()
df_2026 = df_2026[columns].copy()

# Combine the two years
df = pd.concat([df_2025, df_2026], ignore_index=True)

# Clean data types
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
df["Total_AE_Attendances"] = pd.to_numeric(
    df["Total_AE_Attendances"], errors="coerce"
)
df["Org Code"] = df["Org Code"].astype("string").str.strip()

# Remove rows missing essential information
df = df.dropna(
    subset=["Month", "Org Code", "Total_AE_Attendances"]
)

# Check for duplicate provider-month records
duplicates = df.duplicated(
    subset=["Month", "Org Code"], keep=False
)

print("Combined provider-month rows:", len(df))
print("Duplicate provider-month rows:", int(duplicates.sum()))

# Stop if duplicate provider-month records exist
if duplicates.any():
    print("\nDuplicate records found. Please investigate before continuing.")
    print(
        df.loc[duplicates]
        .sort_values(["Month", "Org Code"])
        .to_string(index=False)
    )
    raise SystemExit("Fix duplicates before saving the combined dataset.")

# Aggregate attendance by month
monthly = (
    df.groupby("Month")
    .agg(
        Total_AE_Attendances=("Total_AE_Attendances", "sum"),
        Provider_Count=("Org Code", "nunique"),
    )
    .reset_index()
    .sort_values("Month")
)

# Save provider-level and monthly datasets
df.to_csv(
    "data/processed/nhs_provider_attendance_2025_2026.csv",
    index=False
)

monthly.to_csv(output_file, index=False)

print("\nNumber of months:", len(monthly))
print("Date range:", monthly["Month"].min(), "to", monthly["Month"].max())
print("\nMonthly attendance and provider counts:")
print(monthly.to_string(index=False))

print("\nMonthly dataset saved to:", output_file)
print(
    "Provider-level dataset saved to:",
    "data/processed/nhs_provider_attendance_2025_2026.csv"
)
id="g8k2np"
