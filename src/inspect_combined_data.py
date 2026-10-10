
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

print("\n--- DATASET OVERVIEW ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Column names:")
print(df.columns.tolist())

print("\n--- REPORTING PERIODS ---")
if "Period" in df.columns:
    print("Unique periods:", df["Period"].nunique())
    print(df["Period"].value_counts(dropna=False).sort_index())

print("\n--- ORGANIZATIONS ---")
if "Org Code" in df.columns:
    print("Unique organization codes:", df["Org Code"].nunique())
    print("Missing organization codes:", df["Org Code"].isna().sum())

if "Org name" in df.columns:
    print("Unique organization names:", df["Org name"].nunique())
    print("\nExample organization names:")
    print(df["Org name"].dropna().drop_duplicates().head(15).to_string(index=False))

print("\n--- DUPLICATE CHECK ---")
if {"Period", "Org Code"}.issubset(df.columns):
    duplicates = df.duplicated(
        subset=["Period", "Org Code"],
        keep=False
    )
    print("Duplicate organization-period rows:", int(duplicates.sum()))

print("\n--- ATTENDANCE COLUMNS ---")
attendance_columns = [
    col for col in df.columns
    if "attendances" in col.lower()
]

for col in attendance_columns:
    values = pd.to_numeric(df[col], errors="coerce")
    print(
        f"{col}: missing={values.isna().sum()}, "
        f"minimum={values.min()}, maximum={values.max()}"
    )

print("\n--- SOURCE FILES ---")
if "Source_File" in df.columns:
    print(df["Source_File"].value_counts())

print("\nValidation complete.")
