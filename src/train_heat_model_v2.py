
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

input_file = Path("data/processed/heat_model_data.csv")
output_dir = Path("data/processed")

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])

df = df.dropna(
    subset=[
        "Total_AE_Attendances",
        "Avg_Max_Temp_C",
        "Hot_Days"
    ]
).sort_values("Month").reset_index(drop=True)

# Previous month's attendance
df["Lag_1"] = df["Total_AE_Attendances"].shift(1)
df["Month_Number"] = df["Month"].dt.month

df = df.dropna().reset_index(drop=True)

features = [
    "Month_Number",
    "Lag_1",
    "Avg_Max_Temp_C",
    "Hot_Days"
]
target = "Total_AE_Attendances"

# Keep the final 3 months for testing
train = df.iloc[:-3].copy()
test = df.iloc[-3:].copy()

model = LinearRegression()
model.fit(train[features], train[target])

test["Heat_Model_V2_Prediction"] = np.maximum(
    model.predict(test[features]), 0
)

# Baseline uses the previous month's actual attendance
test["Previous_Month_Baseline"] = test["Lag_1"]

def evaluate(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = (
        np.abs(actual.to_numpy() - predicted.to_numpy())
        / actual.to_numpy()
    ).mean() * 100
    return mae, rmse, mape

print("HEAT MODEL V2")
print("Training months:", len(train))
print("Testing months:", len(test))
print(
    "Test period:",
    test["Month"].min().strftime("%Y-%m"),
    "to",
    test["Month"].max().strftime("%Y-%m")
)

for col, label in [
    ("Heat_Model_V2_Prediction", "Heat Model V2"),
    ("Previous_Month_Baseline", "Previous-month baseline")
]:
    mae, rmse, mape = evaluate(test[target], test[col])
    print(f"\n{label}")
    print(f"MAE: {mae:,.0f}")
    print(f"RMSE: {rmse:,.0f}")
    print(f"MAPE: {mape:.2f}%")

print("\nACTUAL VS PREDICTED")
print(
    test[
        [
            "Month",
            target,
            "Lag_1",
            "Avg_Max_Temp_C",
            "Hot_Days",
            "Heat_Model_V2_Prediction",
            "Previous_Month_Baseline"
        ]
    ].round(0).to_string(index=False)
)

test.to_csv(
    output_dir / "heat_model_v2_predictions.csv",
    index=False
)
print("\nSaved: data/processed/heat_model_v2_predictions.csv")
