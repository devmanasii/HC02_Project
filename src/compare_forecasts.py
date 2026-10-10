
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error

input_file = Path("data/processed/balanced_monthly_attendance.csv")
output_file = Path("data/processed/forecast_comparison.csv")

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])
df = df.sort_values("Month").reset_index(drop=True)

target = "Total_AE_Attendances"

# Forecasts made using only earlier observations
df["Previous_Month_Forecast"] = df[target].shift(1)
df["Previous_Year_Forecast"] = df[target].shift(12)

# Evaluate on the final 6 months: March–August 2026
test = df.tail(6).copy()

def evaluate(actual, predicted):
    valid = actual.notna() & predicted.notna()
    actual = actual[valid]
    predicted = predicted[valid]

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = (np.abs(actual - predicted) / actual).mean() * 100

    return mae, rmse, mape

print("FORECAST COMPARISON")
print("Test period:", test["Month"].min().date(), "to",
      test["Month"].max().date())

for column, label in [
    ("Previous_Month_Forecast", "Previous-month baseline"),
    ("Previous_Year_Forecast", "Previous-year seasonal baseline"),
]:
    mae, rmse, mape = evaluate(test[target], test[column])
    print(f"\n{label}")
    print(f"MAE:  {mae:,.0f}")
    print(f"RMSE: {rmse:,.0f}")
    print(f"MAPE: {mape:.2f}%")

print("\nACTUAL VS FORECAST")
print(
    test[
        [
            "Month",
            target,
            "Previous_Month_Forecast",
            "Previous_Year_Forecast",
        ]
    ].to_string(index=False)
)

test.to_csv(output_file, index=False)
print("\nSaved to:", output_file)
id="p8x2mz"

