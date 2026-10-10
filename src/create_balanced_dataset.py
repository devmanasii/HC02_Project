
import pandas as pd
from pathlib import Path

input_file = Path(
    "data/processed/nhs_provider_attendance_2025_2026.csv"
)

output_file = Path(
    "data/processed/balanced_monthly_attendance.csv"
)

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])

# Count the number of months reported by each provider
months_per_provider = df.groupby("Org Code")["Month"].nunique()

# Keep providers with records in all 20 months
complete_providers = months_per_provider[
    months_per_provider == 20
].index

balanced = df[df["Org Code"].isin(complete_providers)].copy()

# Aggregate attendance for the same set of providers
monthly = (
    balanced.groupby("Month")
    .agg(
        Total_AE_Attendances=("Total_AE_Attendances", "sum"),
        Provider_Count=("Org Code", "nunique"),
    )
    .reset_index()
    .sort_values("Month")
)

print("Total providers in source:", df["Org Code"].nunique())
print("Providers reporting in all 20 months:", len(complete_providers))
print("Monthly records in balanced dataset:", len(monthly))
print("\nMonthly provider counts:")
print(monthly[["Month", "Provider_Count"]].to_string(index=False))

if len(monthly) != 20:
    raise ValueError("Expected 20 monthly records.")

if not (monthly["Provider_Count"] == len(complete_providers)).all():
    raise ValueError("Provider counts are not consistent.")

output_file.parent.mkdir(parents=True, exist_ok=True)
monthly.to_csv(output_file, index=False)

print("\nSaved to:", output_file)
print("\nMonthly attendance totals:")
print(monthly.to_string(index=False))
id="e9v2xk"

