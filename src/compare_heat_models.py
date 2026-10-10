
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error

folder = Path("data/processed")

actual = pd.read_csv(folder / "balanced_monthly_attendance.csv")
actual["Month"] = pd.to_datetime(actual["Month"])
actual = actual.sort_values("Month").reset_index(drop=True)

actual["Previous_Month"] = actual["Total_AE_Attendances"].shift(1)
actual["Previous_Year"] = actual["Total_AE_Attendances"].shift(12)

heat = pd.read_csv(folder / "heat_model_predictions.csv")
heat["Month"] = pd.to_datetime(heat["Month"])

comparison = actual.merge(
    heat[["Month", "Heat_Model_Prediction"]],
    on="Month",
    how="inner"
)

# Previous-year values are not available for these 2025 test months.
# Compare all methods on the same months using available baselines.
comparison = comparison.dropna(
    subset=["Previous_Month", "Heat_Model_Prediction"]
).copy()

def evaluate(actual_values, predictions):
    mae = mean_absolute_error(actual_values, predictions)
    rmse = np.sqrt(mean_squared_error(actual_values, predictions))
    mape = (
        np.abs(actual_values.to_numpy() - predictions.to_numpy())
        / actual_values.to_numpy()
    ).mean() * 100
    return mae, rmse, mape

print("FAIR MODEL COMPARISON")
print("Test months:", len(comparison))
print(
    "Period:",
    comparison["Month"].min().strftime("%Y-%m"),
    "to",
    comparison["Month"].max().strftime("%Y-%m")
)

models = {
    "Previous-month baseline": "Previous_Month",
    "Heat model": "Heat_Model_Prediction",
}

results = []

for name, column in models.items():
    mae, rmse, mape = evaluate(
        comparison["Total_AE_Attendances"],
        comparison[column]
    )

    results.append({
        "Model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE_Percent": round(mape, 2)
    })

results_df = pd.DataFrame(results)
print("\nMETRICS")
print(results_df.to_string(index=False))

comparison.to_csv(
    folder / "heat_model_fair_comparison_predictions.csv",
    index=False
)

results_df.to_csv(
    folder / "heat_model_fair_comparison_metrics.csv",
    index=False
)

print("\nSaved comparison files in data/processed/")
print(
    "Note: previous-year baseline excluded because "
    "the test months are in 2025."
)

