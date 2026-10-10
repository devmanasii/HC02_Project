
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

root = Path(__file__).resolve().parent.parent

data = pd.read_csv(
    root / "data" / "processed" / "heat_model_data_2023_2026.csv"
)
pred = pd.read_csv(root / "outputs" / "xgboost_predictions.csv")

data["Month"] = pd.to_datetime(data["Month"])
pred["Month"] = pd.to_datetime(pred["Month"])

data = data.sort_values("Month").drop_duplicates("Month")
data["Previous_Month_Attendance"] = data["Total_AE_Attendances"].shift(1)

comparison = pred.merge(
    data[["Month", "Previous_Month_Attendance"]],
    on="Month",
    how="left"
).dropna()

actual = comparison["Actual_Attendance"].to_numpy()
xgb = comparison["Predicted_Attendance"].to_numpy()
baseline = comparison["Previous_Month_Attendance"].to_numpy()

def evaluate(name, prediction):
    mae = mean_absolute_error(actual, prediction)
    rmse = np.sqrt(mean_squared_error(actual, prediction))
    mape = np.mean(
        np.abs(actual - prediction) / np.maximum(np.abs(actual), 1)
    ) * 100
    return {
        "Model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE_Percent": round(mape, 2)
    }

results = pd.DataFrame([
    evaluate("XGBoost", xgb),
    evaluate("Previous-month baseline", baseline)
])

print("\nFAIR COMPARISON ON THE SAME TEST MONTHS")
print(results.to_string(index=False))

results.to_csv(root / "outputs" / "fair_model_comparison.csv", index=False)
print("\nSaved: outputs/fair_model_comparison.csv")