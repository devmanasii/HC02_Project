
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent.parent
folder = root / "data" / "processed"

files = [
    "heat_model_data_2023_2026.csv",
    "heat_model_data_balanced_2023_2026.csv",
    "nhs_monthly_target.csv",
    "nhs_monthly_attendance_2023_2024.csv",
    "nhs_attendance_2025_2026.csv",
    "balanced_monthly_attendance.csv",
]

for name in files:
    path = folder / name

    print("\n" + "=" * 70)
    print("FILE:", name)

    if not path.exists():
        print("Not found")
        continue

    df = pd.read_csv(path)
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())

    month_col = next(
        (c for c in ["Month", "Period"] if c in df.columns), None
    )

    if month_col:
        print("Date range:", df[month_col].min(), "to", df[month_col].max())

    attendance_cols = [
        c for c in df.columns
        if "attendance" in c.lower() and
        any(word in c.lower() for word in ["total", "ae_attendances"])
    ]

    for col in attendance_cols:
        print("\nAttendance column:", col)
        print(df[col].describe().round(2).to_string())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))