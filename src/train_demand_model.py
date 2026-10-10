
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load monthly attendance data
input_file = Path("data/processed/balanced_monthly_attendance.csv")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])
df = df.sort_values("Month").reset_index(drop=True)

target = "Total_AE_Attendances"

# 2. Create historical and calendar features
df["Month_Number"] = df["Month"].dt.month
df["Time_Index"] = np.arange(len(df))
df["Lag_1"] = df[target].shift(1)
df["Lag_2"] = df[target].shift(2)
df["Lag_3"] = df[target].shift(3)
df["Rolling_Mean_3"] = df[target].shift(1).rolling(3).mean()

features = [
    "Month_Number",
    "Time_Index",
    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Rolling_Mean_3",
]

model_data = df.dropna(subset=features + [target]).copy()

# 3. Chronological split: first 12 rows train, last 5 test
split_index = len(model_data) - 5
train = model_data.iloc[:split_index]
test = model_data.iloc[split_index:]

X_train = train[features]
y_train = train[target]
X_test = test[features]
y_test = test[target]

# 4. Train two models
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=3,
        min_samples_leaf=2,
        random_state=42
    ),
}

results = []
predictions = test[["Month", target]].copy()

# Previous-month baseline for the same test months
predictions["Previous_Month_Baseline"] = test["Lag_1"].values

for name, model in models.items():
    model.fit(X_train, y_train)
    predicted = model.predict(X_test)
    predicted = np.maximum(predicted, 0)

    predictions[name.replace(" ", "_")] = predicted

    mae = mean_absolute_error(y_test, predicted)
    rmse = np.sqrt(mean_squared_error(y_test, predicted))
    mape = (np.abs(y_test.to_numpy() - predicted)
            / y_test.to_numpy()).mean() * 100

    results.append({
        "Model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE_Percent": round(mape, 2),
    })

# Evaluate baseline on the same test months
baseline = predictions["Previous_Month_Baseline"]
baseline_mae = mean_absolute_error(y_test, baseline)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline))
baseline_mape = (
    np.abs(y_test.to_numpy() - baseline.to_numpy())
    / y_test.to_numpy()
).mean() * 100

results.append({
    "Model": "Previous-month baseline",
    "MAE": round(baseline_mae, 2),
    "RMSE": round(baseline_rmse, 2),
    "MAPE_Percent": round(baseline_mape, 2),
})

# 5. Save evaluation and predictions
results_df = pd.DataFrame(results).sort_values("MAE")
results_df.to_csv(output_dir / "model_evaluation.csv", index=False)
predictions.to_csv(output_dir / "model_predictions.csv", index=False)

print("TRAINING COMPLETE")
print("Training observations:", len(train))
print("Testing observations:", len(test))
print("Test period:",
      test["Month"].min().strftime("%Y-%m"),
      "to",
      test["Month"].max().strftime("%Y-%m"))

print("\nMODEL COMPARISON (lower is better)")
print(results_df.to_string(index=False))

print("\nACTUAL VS PREDICTED")
print(predictions.round(0).to_string(index=False))

print("\nSaved:")
print("data/processed/model_evaluation.csv")
print("data/processed/model_predictions.csv")