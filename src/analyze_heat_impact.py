
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "heat_model_data_verified.csv"
OUTPUT_DIR = ROOT / "outputs"

df = pd.read_csv(DATA_FILE)

# Correlations are exploratory, not proof of causation
weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

correlations = (
    df[weather_columns + ["Total_AE_Attendances"]]
    .corr(numeric_only=True)["Total_AE_Attendances"]
    .drop("Total_AE_Attendances")
    .sort_values(ascending=False)
)

print("\n=== WEATHER AND HOSPITAL ATTENDANCE CORRELATION ===")
print(correlations.to_string())

# Compare months with more hot days against months with fewer hot days
threshold = df["Hot_Days"].median()
df["Heat_Group"] = df["Hot_Days"].apply(
    lambda value: "Higher-hot-days months"
    if value > threshold else "Lower-hot-days months"
)

summary = df.groupby("Heat_Group").agg(
    Months=("Total_AE_Attendances", "count"),
    Average_Attendance=("Total_AE_Attendances", "mean"),
    Average_Max_Temperature=("Avg_Max_Temp_C", "mean"),
    Average_Hot_Days=("Hot_Days", "mean"),
).round(2)

print("\n=== COMPARISON BY HOT-DAY GROUP ===")
print(summary.to_string())

correlations.to_csv(OUTPUT_DIR / "heat_correlations.csv")
summary.to_csv(OUTPUT_DIR / "heat_impact_summary.csv")

print("\nSaved heat_correlations.csv and heat_impact_summary.csv")