
import pandas as pd
from pathlib import Path

file_path = Path(
    "data/processed/nhs_provider_attendance_2025_2026.csv"
)

df = pd.read_csv(file_path)
df["Month"] = pd.to_datetime(df["Month"])

# Get the provider sets for each year
providers_2025 = set(
    df.loc[df["Month"].dt.year == 2025, "Org Code"].dropna()
)

providers_2026 = set(
    df.loc[df["Month"].dt.year == 2026, "Org Code"].dropna()
)

common_providers = providers_2025.intersection(providers_2026)
only_2025 = providers_2025 - providers_2026
only_2026 = providers_2026 - providers_2025

print("PROVIDER CONSISTENCY CHECK")
print("Unique providers in 2025:", len(providers_2025))
print("Unique providers in 2026:", len(providers_2026))
print("Providers present in both years:", len(common_providers))
print("Providers found only in 2025:", len(only_2025))
print("Providers found only in 2026:", len(only_2026))

# Compare monthly attendance for common providers only
common_df = df[df["Org Code"].isin(common_providers)]

monthly_common = (
    common_df.groupby("Month")
    .agg(
        Attendance=("Total_AE_Attendances", "sum"),
        Provider_Count=("Org Code", "nunique"),
    )
    .reset_index()
    .sort_values("Month")
)

print("\nMONTHLY ATTENDANCE FOR COMMON PROVIDERS")
print(monthly_common.to_string(index=False))

output_file = Path(
    "data/processed/common_provider_monthly_attendance.csv"
)
monthly_common.to_csv(output_file, index=False)

print("\nSaved to:", output_file)
id="c8v5ws"

