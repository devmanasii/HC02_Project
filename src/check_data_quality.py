
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "nhs_monthly_combined.csv"
)

df = pd.read_csv(INPUT_FILE, low_memory=False)

# 1. Inspect all unusual period labels
print("\n--- UNUSUAL PERIOD LABELS ---")

period_text = df["Period"].astype(str).str.strip()

unusual = ~period_text.str.contains(
    r"MSitAE-", case=False, regex=True
)

print(
    df.loc[
        unusual,
        ["Period", "Org Code", "Org name", "Source_File"]
    ].to_string(index=False)
)

# 2. Inspect duplicate organization-period keys
print("\n--- DUPLICATE ORGANIZATION-PERIOD ROWS ---")

duplicate_mask = df.duplicated(
    subset=["Period", "Org Code"],
    keep=False
)

duplicate_rows = df.loc[duplicate_mask].sort_values(
    ["Period", "Org Code", "Source_File"]
)

print(
    duplicate_rows[
        ["Period", "Org Code", "Org name", "Source_File"]
    ].to_string(index=False)
)

# 3. Check whether duplicate keys have identical measures
key_columns = ["Period", "Org Code"]

measure_columns = [
    c for c in df.columns
    if c not in key_columns + ["Source_File", "Parent Org", "Org name"]
]

for (period, org_code), group in duplicate_rows.groupby(key_columns):
    print(f"\nKey: {period} | {org_code}")
    print("Number of rows:", len(group))
    print(
        "Distinct measurement rows:",
        len(group[measure_columns].drop_duplicates())
    )

print("\nInspection complete. No rows have been deleted.")