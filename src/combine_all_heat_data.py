
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Define file paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

HISTORICAL_FILE = DATA_DIR / "heat_model_data_2023_2024.csv"
RECENT_FILE = DATA_DIR / "heat_model_data.csv"
OUTPUT_FILE = DATA_DIR / "heat_model_data_2023_2026.csv"

# --------------------------------------------------
# 2. Check that input files exist
# --------------------------------------------------
for file in [HISTORICAL_FILE, RECENT_FILE]:
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file}")

# --------------------------------------------------
# 3. Read datasets
# --------------------------------------------------
historical = pd.read_csv(HISTORICAL_FILE)
recent = pd.read_csv(RECENT_FILE)

print("Historical dataset rows:", len(historical))
print("Recent dataset rows:", len(recent))

# --------------------------------------------------
# 4. Define required modelling columns
# --------------------------------------------------
COMMON_COLUMNS = [
    "Month",
    "Total_AE_Attendances",
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

for name, df in [
    ("2023–2024", historical),
    ("2025–2026", recent),
]:
    missing_columns = [
        col for col in COMMON_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{name} dataset is missing columns: {missing_columns}"
        )

# Keep only common modelling columns.
historical = historical[COMMON_COLUMNS].copy()
recent = recent[COMMON_COLUMNS].copy()

# --------------------------------------------------
# 5. Normalize Month values
# --------------------------------------------------
def normalize_month(series, dataset_name):
    original = series.astype(str).str.strip()

    # Convert common date formats to YYYY-MM.
    parsed = pd.to_datetime(original, errors="coerce")

    # Handle values such as YYYY-MM explicitly.
    year_month = original.str.fullmatch(r"\d{4}-\d{2}")

    normalized = pd.Series(index=original.index, dtype="object")
    normalized.loc[year_month] = original.loc[year_month]

    other = ~year_month
    normalized.loc[other] = parsed.loc[other].dt.strftime("%Y-%m")

    invalid = normalized.isna() | ~normalized.str.fullmatch(
        r"\d{4}-(0[1-9]|1[0-2])", na=False
    )

    if invalid.any():
        bad_values = original.loc[invalid].tolist()
        raise ValueError(
            f"Invalid Month values in {dataset_name}: {bad_values}"
        )

    return normalized

historical["Month"] = normalize_month(
    historical["Month"], "2023–2024 dataset"
)

recent["Month"] = normalize_month(
    recent["Month"], "2025–2026 dataset"
)

# --------------------------------------------------
# 6. Combine datasets
# --------------------------------------------------
combined = pd.concat(
    [historical, recent],
    ignore_index=True,
)

combined = combined.sort_values("Month").reset_index(drop=True)

# --------------------------------------------------
# 7. Check duplicate months
# --------------------------------------------------
duplicate_mask = combined["Month"].duplicated(keep=False)

if duplicate_mask.any():
    duplicate_months = sorted(
        combined.loc[duplicate_mask, "Month"].unique().tolist()
    )

    print("\nDuplicate months detected:")
    print(duplicate_months)

    raise ValueError(
        "Duplicate months found. Check the source datasets before combining."
    )

# --------------------------------------------------
# 8. Check expected timeline
# --------------------------------------------------
expected_months = pd.period_range(
    start="2023-01",
    end="2026-08",
    freq="M",
).astype(str).tolist()

actual_months = combined["Month"].tolist()

missing_months = sorted(
    set(expected_months) - set(actual_months)
)

unexpected_months = sorted(
    set(actual_months) - set(expected_months)
)

print("\n--- TIMELINE DIAGNOSTIC ---")
print("Actual row count:", len(combined))
print("Expected row count:", len(expected_months))
print("First month:", combined["Month"].iloc[0])
print("Last month:", combined["Month"].iloc[-1])
print("Missing months:", missing_months)
print("Unexpected months:", unexpected_months)

if missing_months or unexpected_months:
    raise ValueError(
        "Timeline check failed. Review the diagnostic output above."
    )

# --------------------------------------------------
# 9. Check missing values
# --------------------------------------------------
missing_values = combined.isnull().sum()

print("\nMissing values by column:")
print(missing_values.to_string())

if missing_values.sum() > 0:
    print(
        "\nWARNING: Missing values exist. "
        "The combined dataset will be saved for inspection."
    )

# --------------------------------------------------
# 10. Save combined dataset
# --------------------------------------------------
combined.to_csv(OUTPUT_FILE, index=False)

print("\nSUCCESS: Combined dataset created.")
print("Total rows:", len(combined))
print("Total columns:", len(combined.columns))
print("First month:", combined["Month"].iloc[0])
print("Last month:", combined["Month"].iloc[-1])
print("Duplicate months:", combined["Month"].duplicated().sum())
print("Total missing values:", int(missing_values.sum()))
print("Output file:", OUTPUT_FILE)

print("\nFirst five rows:")
print(combined.head().to_string(index=False))

print("\nLast five rows:")
print(combined.tail().to_string(index=False))