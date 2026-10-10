
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "heat_model_data_verified.csv"
)
MODEL_PATH = PROJECT_DIR / "outputs" / "best_model.pkl"

TARGET = "Total_AE_Attendances"

df = pd.read_csv(DATA_PATH)
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")

df = (
    df.dropna(subset=["Month", TARGET])
    .sort_values("Month")
    .reset_index(drop=True)
)

# The training script needs two previous attendance records.
if len(df) < 2:
    raise ValueError("At least two monthly records are required.")

# Create the feature row for the next month.
last = df.iloc[-1]
previous = df.iloc[-2]

next_month = last["Month"] + pd.DateOffset(months=1)

features = {
    "Provider_Count": last["Provider_Count"],
    "year": next_month.year,
    "month": next_month.month,
    "month_sin": np.sin(2 * np.pi * next_month.month / 12),
    "month_cos": np.cos(2 * np.pi * next_month.month / 12),
    "attendance_lag_1": last[TARGET],
    "attendance_lag_2": previous[TARGET],
}

weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

for column in weather_columns:
    if column in df.columns:
        features[f"{column}_lag_1"] = last[column]

# Load the newly trained model.
model = joblib.load(MODEL_PATH)

# Keep feature names/order consistent with the training pipeline.
feature_names = list(
    model.named_steps["preprocessing"].feature_names_in_
)

X_future = pd.DataFrame([features]).reindex(
    columns=feature_names
)

prediction = float(model.predict(X_future)[0])

print("\nHEATCARE - Hospital Demand Forecast")
print("-----------------------------------")
print("Forecast month:", next_month.strftime("%B %Y"))
print(f"Predicted A&E attendances: {prediction:,.0f}")
print("Status: Experimental forecast; validate before real-world use.")

# Save the result for later backend/dashboard integration.
output_path = PROJECT_DIR / "outputs" / "next_month_prediction.csv"

pd.DataFrame([{
    "Forecast_Month": next_month.strftime("%Y-%m"),
    "Predicted_AE_Attendances": round(prediction),
    "Model": "XGBoost"
}]).to_csv(output_path, index=False)

print("Saved prediction:", output_path)