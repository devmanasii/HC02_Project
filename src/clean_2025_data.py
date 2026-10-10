
import pandas as pd
from pathlib import Path

input_file = Path("data/processed/nhs_2025_combined.csv")
output_file = Path("data/processed/nhs_2025_cleaned.csv")

df = pd.read_csv(input_file, low_memory=False)

print("Original rows:", len(df))

# Remove summary rows such as TOTAL or Total.
summary_mask = (
    df["Period"]
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("TOTAL")
)

print("Summary rows found:", int(summary_mask.sum()))

df = df.loc[~summary_mask].copy()

# Check for missing organization identifiers.
print(
    "Rows with missing Org Code:",
    int(df["Org Code"].isna().sum())
)

# Check duplicate organization-period records.
duplicate_mask = df.duplicated(
    subset=["Period", "Org Code"],
    keep=False
)

print(
    "Rows involved in duplicate Period + Org Code records:",
    int(duplicate_mask.sum())
)

# Convert attendance measures to numeric values.
attendance_columns = [
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
]

for column in attendance_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

print(
    "\nMissing values in attendance columns:"
)
print(df[attendance_columns].isna().sum().to_string())

# Keep all remaining rows for now.
# Do not remove duplicate rows automatically until inspected.
output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\nCLEANING CHECK COMPLETE")
print("Rows after removing summary rows:", len(df))
print("Unique reporting periods:", df["Period"].nunique())
print("\nRows per reporting period:")
print(df["Period"].value_counts().sort_index().to_string())

print("\nSaved to:", output_file)