
from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent

source = (
    project_dir
    / "data"
    / "processed"
    / "heat_model_data_verified.csv"
)

output = project_dir / "monthly_attendance_supabase.csv"

df = pd.read_csv(source)

df = df.rename(columns={
    "Month": "month",
    "Total_AE_Attendances": "total_ae_attendances",
    "Provider_Count": "provider_count",
    "Avg_Max_Temp_C": "avg_max_temp_c",
    "Avg_Min_Temp_C": "avg_min_temp_c",
    "Highest_Temp_C": "highest_temp_c",
    "Avg_Humidity_Pct": "avg_humidity_pct",
    "Hot_Days": "hot_days",
})

required = [
    "month",
    "total_ae_attendances",
    "provider_count",
    "avg_max_temp_c",
    "avg_min_temp_c",
    "highest_temp_c",
    "avg_humidity_pct",
    "hot_days",
]

missing = [column for column in required if column not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df[required].copy()
df["month"] = pd.to_datetime(
    df["month"], errors="coerce"
).dt.strftime("%Y-%m-%d")

if df.isna().any().any():
    raise ValueError(
        "Missing or invalid values found. Check the source CSV first."
    )

if df["month"].duplicated().any():
    raise ValueError("Duplicate months found in the CSV.")

df.to_csv(output, index=False)

print("CSV prepared successfully.")
print("Rows:", len(df))
print("Output:", output)
print(df.head().to_string(index=False))
