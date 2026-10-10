
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "original" / "nhs_historical"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATTENDANCE_COLUMNS = [
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
]

records = []
errors = []

for year in [2023, 2024]:
    year_dir = INPUT_DIR / str(year)

    if not year_dir.exists():
        errors.append(f"Missing folder: {year_dir}")
        continue

    files = sorted(year_dir.glob("*.csv"))

    print(f"\n{year}: found {len(files)} CSV files")

    for file in files:
        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()

            required = [
                "Org Code",
                "Org name",
                *ATTENDANCE_COLUMNS,
            ]

            missing = [col for col in required if col not in df.columns]

            if missing:
                errors.append(
                    f"{file.name}: missing columns {missing}"
                )
                continue

            for col in ATTENDANCE_COLUMNS:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Derive the month from the filename's actual data period.
            period = df["Period"].dropna().astype(str)

            if period.empty:
                errors.append(f"{file.name}: no Period value")
                continue

            period_text = period.iloc[0].upper()

            month_names = {
                "JANUARY": "01", "FEBRUARY": "02",
                "MARCH": "03", "APRIL": "04",
                "MAY": "05", "JUNE": "06",
                "JULY": "07", "AUGUST": "08",
                "SEPTEMBER": "09", "OCTOBER": "10",
                "NOVEMBER": "11", "DECEMBER": "12",
            }

            month_number = next(
                (
                    number for name, number in month_names.items()
                    if name in period_text
                ),
                None,
            )

            if month_number is None:
                errors.append(
                    f"{file.name}: cannot identify month from "
                    f"Period={period_text}"
                )
                continue

            month = f"{year}-{month_number}"

            df["Total_AE_Attendances"] = (
                df[ATTENDANCE_COLUMNS].sum(axis=1, min_count=3)
            )

            df["Month"] = month
            df["Source_File"] = file.name

            records.append(
                df[
                    [
                        "Month",
                        "Org Code",
                        "Org name",
                        *ATTENDANCE_COLUMNS,
                        "Total_AE_Attendances",
                        "Source_File",
                    ]
                ]
            )

        except Exception as exc:
            errors.append(f"{file.name}: {exc}")

if records:
    combined = pd.concat(records, ignore_index=True)

    provider_output = (
        OUTPUT_DIR / "nhs_provider_attendance_2023_2024.csv"
    )
    combined.to_csv(provider_output, index=False)

    monthly_output = (
        OUTPUT_DIR / "nhs_monthly_attendance_2023_2024.csv"
    )

    monthly = (
        combined.groupby("Month", as_index=False)
        ["Total_AE_Attendances"]
        .sum(min_count=1)
    )
    monthly.to_csv(monthly_output, index=False)

    print("\nPROCESSING COMPLETE")
    print("Provider rows:", len(combined))
    print("Unique months:", combined["Month"].nunique())
    print("Provider file:", provider_output)
    print("Monthly file:", monthly_output)
    print("\nMonthly attendance totals:")
    print(monthly.to_string(index=False))

else:
    print("\nNo data was processed.")

if errors:
    print("\nWARNINGS / ERRORS:")
    for error in errors:
        print("-", error)