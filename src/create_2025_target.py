
import pandas as pd
from pathlib import Path

input_file = Path("data/processed/nhs_2025_cleaned.csv")
output_file = Path("data/processed/nhs_2025_target.csv")

df = pd.read_csv(input_file, low_memory=False)

# Convert the reporting period into a real date.
month_names = {
    "JANUARY": "01",
    "FEBRUARY": "02",
    "MARCH": "03",
    "APRIL": "04",
    "MAY": "05",
    "JUNE": "06",
    "JULY": "07",
    "AUGUST": "08",
    "SEPTEMBER": "09",
    "OCTOBER": "10",
    "NOVEMBER": "11",
    "DECEMBER": "12",
}

def parse_period(period):
    parts = str(period).strip().upper().split("-")

    # Expected format: MSITAE-JANUARY-2025
    if len(parts) != 3:
        return pd.NaT

    month = month_names.get(parts[1])
    year = parts[2]

    if month is None:
        return pd.NaT

    return pd.to_datetime(
        f"{year}-{month}-01",
        errors="coerce"
    )

df["Month"] = df["Period"].apply(parse_period)

# Calculate total A&E attendances for each provider.
attendance_columns = [
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
]

df["Total_AE_Attendances"] = df[attendance_columns].sum(axis=1)

print("Rows:", len(df))
print("Unique months:", df["Month"].nunique())
print("Invalid month values:", int(df["Month"].isna().sum()))
print(
    "Missing attendance targets:",
    int(df["Total_AE_Attendances"].isna().sum())
)

print("\nMonthly provider-row counts:")
print(
    df.groupby("Month").size().to_string()
)

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("\n2025 attendance target saved to:", output_file)
print("\nFirst 5 rows:")
print(
    df[["Month", "Org Code", "Org name", "Total_AE_Attendances"]]
    .head()
    .to_string(index=False)
)