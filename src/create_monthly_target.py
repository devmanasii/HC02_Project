
import pandas as pd
from pathlib import Path

input_file = Path("data/processed/nhs_monthly_cleaned.csv")
output_file = Path("data/processed/nhs_monthly_target.csv")

df = pd.read_csv(input_file)

# Convert the reporting period into a readable month
df["Month"] = (
    df["Period"]
    .str.replace("MSitAE-", "", regex=False)
)

df["Month"] = pd.to_datetime(
    df["Month"],
    format="%B-%Y",
    errors="coerce"
)

# Create total monthly A&E attendances across the three categories
attendance_columns = [
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
]

df["Total_AE_Attendances"] = df[attendance_columns].sum(axis=1)

# Check whether any reporting periods failed to convert
if df["Month"].isna().any():
    print("Warning: Some reporting periods could not be parsed.")
    print(df.loc[df["Month"].isna(), "Period"].unique())

# Keep useful fields while retaining the original attendance categories
columns_to_keep = [
    "Month",
    "Org Code",
    "Org name",
    "Total_AE_Attendances",
    *attendance_columns,
    "Source_File",
]

result = df[columns_to_keep].sort_values(
    ["Month", "Org Code"]
)

result.to_csv(output_file, index=False)

print("Monthly target dataset created.")
print("Rows:", len(result))
print("Unique months:", result["Month"].nunique())
print("Missing total attendance values:",
      result["Total_AE_Attendances"].isna().sum())
print("Saved to:", output_file)

print("\nSample:")
print(result.head(10).to_string(index=False))