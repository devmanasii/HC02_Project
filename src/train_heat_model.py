
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

input_file = Path("data/processed/heat_model_data.csv")
output_dir = Path("data/processed")

df = pd.read_csv(input_file)
df = df.dropna(
    subset=["Total_AE_Attendances", "Avg_Max_Temp_C",
            "Hot_Days"]
).copy()

df["Month"] = pd.to_datetime(df["Month"])
df = df.sort_values("Month").reset_index(drop=True)
df["Month_Number"] = df["Month"].dt.month

target = "Total_AE_Attendances"

# Use only the first 9 months for training and last 3 for testing.
features = ["Month_Number", "Avg_Max_Temp_C", "Hot_Days"]
train = df.iloc[:9]
test = df.iloc[9:].copy()

model = LinearRegression()
model.fit(train[features], train[target])

test["Heat_Model_Prediction"] = np.maximum(
    model.predict(test[features]), 0
)

# Previous-year seasonal baseline is not available for this
# one-year weather dataset, so compare against previous-month
# attendance on the same test months.
test["Previous_Month_Baseline"] = test[target].shift(1)

# The first test month uses the previous actual month, which
# is available in the chronological series.
for i in test.index:
    previous_index = i - 1
    test.loc[i, "Previous_Month_Baseline"] = df.loc[
        previous_index, target
    ]

def metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = (
        np.abs(actual.to_numpy() - predicted.to_numpy())
        / actual.to_numpy()
    ).mean() * 100
    return mae, rmse, mape

print("HEAT MODEL EXPERIMENT")
print("Training months:", len(train))
print("Testing months:", len(test))
print("Test period:",
      test["Month"].min().strftime("%Y-%m"),
      "to", test["Month"].max().strftime("%Y-%m"))

for column, label in [
    ("Heat_Model_Prediction", "Weather-informed Linear Regression"),
    ("Previous_Month_Baseline", "Previous-month baseline"),
]:
    mae, rmse, mape = metrics(test[target], test[column])
    print(f"\n{label}")
    print(f"MAE: {mae:,.0f}")
    print(f"RMSE: {rmse:,.0f}")
    print(f"MAPE: {mape:.2f}%")

print("\nACTUAL VS PREDICTED")
print(test[
    ["Month", target, "Avg_Max_Temp_C", "Hot_Days",
     "Heat_Model_Prediction", "Previous_Month_Baseline"]
].round(0).to_string(index=False))

test.to_csv(output_dir / "heat_model_predictions.csv", index=False)
print("\nSaved: data/processed/heat_model_predictions.csv")