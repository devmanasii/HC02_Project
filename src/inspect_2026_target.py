
import pandas as pd
from pathlib import Path

file_path = Path("data/processed/nhs_monthly_target.csv")

df = pd.read_csv(file_path)
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")

print("2026 NHS ATTENDANCE DATA CHECK")
print("Total provider-month rows:", len(df))
print("Unique months:", df["Month"].nunique())
print("Date range:", df["Month"].min(), "to", df["Month"].max())
print("Missing month values:", df["Month"].isna().sum())
print(
    "Missing attendance targets:",
    df["Total_AE_Attendances"].isna().sum()
)

print("\nMonthly provider-row counts:")
print(df.groupby("Month").size().to_string())

print("\nMonthly attendance totals:")
print(
    df.groupby("Month")["Total_AE_Attendances"]
    .sum()
    .to_string()
)
