
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pathlib import Path
import numpy as np

file_path = Path("data/processed/heat_model_data.csv")
df = pd.read_csv(file_path, parse_dates=["Month"])
df = df.sort_values("Month").reset_index(drop=True)

target = "Total_AE_Attendances"
features = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days"
]

# Train only on 2025 data
train = df[df["Month"].dt.year == 2025].copy()

# Evaluate on summer 2026
test = df[
    (df["Month"] >= "2026-05-01") &
    (df["Month"] <= "2026-08-01")
].copy()

if len(train) < 6 or len(test) == 0:
    raise ValueError("Not enough training or test data.")

# Model using weather features
model = LinearRegression()
model.fit(train[features], train[target])
test["Weather_Model_Prediction"] = model.predict(test[features])

# Baseline: use the same month's attendance from the previous year
previous_year = df[["Month", target]].copy()
previous_year["Month"] = previous_year["Month"] + pd.DateOffset(years=1)
previous_year = previous_year.rename(
    columns={target: "Previous_Year_Prediction"}
)

test = test.merge(previous_year, on="Month", how="left")

# Metrics
def show_metrics(name, actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    print(f"{name}:")
    print(f"  MAE:  {mae:,.0f}")
    print(f"  RMSE: {rmse:,.0f}")

print("Training period:", train["Month"].min().strftime("%Y-%m"),
      "to", train["Month"].max().strftime("%Y-%m"))
print("Test period:", test["Month"].min().strftime("%Y-%m"),
      "to", test["Month"].max().strftime("%Y-%m"))

print("\nActual vs predictions:")
print(test[[
    "Month",
    target,
    "Weather_Model_Prediction",
    "Previous_Year_Prediction",
    "Hot_Days"
]].to_string(index=False))

print("\nEvaluation:")
show_metrics(
    "Weather model",
    test[target],
    test["Weather_Model_Prediction"]
)

valid = test.dropna(subset=["Previous_Year_Prediction"])
show_metrics(
    "Previous-year baseline",
    valid[target],
    valid["Previous_Year_Prediction"]
)

output = Path("data/processed/summer_2026_evaluation.csv")
test.to_csv(output, index=False)
print("\nSaved:", output)