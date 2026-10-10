
from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
data_dir = project_dir / "data" / "processed"

files = [
    "nhs_monthly_cleaned.csv",
    "nhs_monthly_target.csv",
    "weather_cleaned.csv",
    "monthly_weather.csv",
    "heat_model_data_2023_2026.csv",
    "heat_model_fair_comparison_metrics.csv",
]

for filename in files:
    path = data_dir / filename

    print("\n" + "=" * 80)
    print("FILE:", filename)

    if not path.exists():
        print("File not found.")
        continue

    try:
        df = pd.read_csv(path)

        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist())
        print("\nFirst 3 rows:")
        print(df.head(3).to_string(index=False))

    except Exception as error:
        print("Error:", error)