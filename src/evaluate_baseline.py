
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Load forecasting dataset
input_file = Path("data/processed/forecasting_data_2025.csv")
df = pd.read_csv(input_file)

df["Month"] = pd.to_datetime(df["Month"])
df = df.sort_values("Month").reset_index(drop=True)

# The previous-month forecast starts from February
evaluation = df.dropna(
    subset=[
        "Previous_Month_Attendance",
        "Total_AE_Attendances"
    ]
).copy()

# Actual and predicted attendance
actual = evaluation["Total_AE_Attendances"]
predicted = evaluation["Previous_Month_Attendance"]

# Calculate evaluation metrics
mae = mean_absolute_error(actual, predicted)
rmse = np.sqrt(mean_squared_error(actual, predicted))
mape = (
    (abs(actual - predicted) / actual).mean()
    * 100
)

print("BASELINE FORECAST EVALUATION")
print("Months evaluated:", len(evaluation))
print(f"MAE:  {mae:,.2f} attendances")
print(f"RMSE: {rmse:,.2f} attendances")
print(f"MAPE: {mape:.2f}%")

# Display actual vs predicted
results = evaluation[
    ["Month", "Total_AE_Attendances"]
].copy()

results["Predicted_Attendance"] = predicted
results["Absolute_Error"] = abs(actual - predicted)

print("\nACTUAL VS PREDICTED")
print(results.to_string(index=False))

# Save results
output_file = Path("data/processed/baseline_forecast_results.csv")
results.to_csv(output_file, index=False)

print("\nResults saved to:", output_file)
id="q5mb3z"

