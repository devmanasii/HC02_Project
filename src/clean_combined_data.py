
import pandas as pd
from pathlib import Path

# Project paths
input_file = Path("data/processed/nhs_monthly_combined.csv")
output_file = Path("data/processed/nhs_monthly_cleaned.csv")

# Load combined dataset
df = pd.read_csv(input_file)

print("Original rows:", len(df))

# Remove summary rows, not individual hospital records
period = df["Period"].astype(str).str.strip().str.upper()
org_code = df["Org Code"].astype(str).str.strip().str.upper()
org_name = df["Org name"].astype(str).str.strip().str.upper()

summary_mask = (
    period.isin(["TOTAL", "TOTAL"])
    | org_code.eq("TOTAL")
    | org_name.eq("TOTAL")
)

print("Summary rows identified:", int(summary_mask.sum()))

# Keep only non-summary rows
cleaned = df.loc[~summary_mask].copy()

# Check duplicate hospital-month records before removing anything
duplicate_mask = cleaned.duplicated(
    subset=["Period", "Org Code"],
    keep=False
)

print("Rows remaining:", len(cleaned))
print("Rows involved in possible hospital-month duplicates:",
      int(duplicate_mask.sum()))

if duplicate_mask.any():
    print("\nReview these possible duplicates:")
    print(
        cleaned.loc[
            duplicate_mask,
            ["Period", "Org Code", "Org name", "Source_File"]
        ].to_string(index=False)
    )

# Save without automatically deleting possible duplicates
cleaned.to_csv(output_file, index=False)

print("\nCleaned dataset saved to:", output_file)
print("Cleaning complete.")