
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "processed" / "heat_model_data_2023_2026.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load dataset
df = pd.read_csv(DATA_FILE)

required_columns = [
    "Month",
    "Total_AE_Attendances",
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

missing = [col for col in required_columns if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df[required_columns].copy()
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")

numeric_columns = required_columns[1:]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = (
    df.dropna()
    .sort_values("Month")
    .drop_duplicates(subset="Month")
    .reset_index(drop=True)
)

if len(df) < 15:
    raise ValueError(
        f"Only {len(df)} valid monthly records. More data is needed."
    )

# 2. Create time and previous-month features
df["Month_Number"] = df["Month"].dt.month
df["Month_Sin"] = np.sin(2 * np.pi * df["Month_Number"] / 12)
df["Month_Cos"] = np.cos(2 * np.pi * df["Month_Number"] / 12)

df["Previous_Month_Attendance"] = df["Total_AE_Attendances"].shift(1)

df = df.dropna().reset_index(drop=True)

features = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
    "Month_Sin",
    "Month_Cos",
    "Previous_Month_Attendance",
]

target = "Total_AE_Attendances"

X = df[features]
y = df[target]

# 3. Chronological split: earlier months train, later months test
split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]
y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("Total usable records:", len(df))
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Training period:", df["Month"].iloc[1:split_index + 1].min().date(),
      "to", df["Month"].iloc[split_index].date())
print("Testing period:", df["Month"].iloc[split_index + 1].date(),
      "to", df["Month"].iloc[-1].date())

# 4. Train only XGBoost
model = XGBRegressor(
    n_estimators=100,
    max_depth=2,
    learning_rate=0.03,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42
)

model.fit(X_train, y_train)

# 5. Evaluate predictions
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

actual = y_test.to_numpy()
mape = np.mean(
    np.abs(actual - predictions) / np.maximum(np.abs(actual), 1)
) * 100

print("\nXGBoost Evaluation")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%")

# 6. Save predictions and metrics

prediction_df = pd.DataFrame({
    "Month": df["Month"].iloc[split_index:].dt.strftime("%Y-%m").to_numpy(),
    "Actual_Attendance": actual,
    "Predicted_Attendance": np.round(predictions).astype(int),
})

prediction_df.to_csv(
    OUTPUT_DIR / "xgboost_predictions.csv", index=False
)

pd.DataFrame([{
    "Model": "XGBoost",
    "MAE": mae,
    "RMSE": rmse,
    "MAPE_Percent": mape,
    "Training_Records": len(X_train),
    "Testing_Records": len(X_test),
}]).to_csv(OUTPUT_DIR / "xgboost_metrics.csv", index=False)

# 7. Save the trained model and its feature list
joblib.dump(
    {"model": model, "features": features},
    OUTPUT_DIR / "best_heat_model.pkl"
)

print("\nSaved successfully:")
print(OUTPUT_DIR / "xgboost_predictions.csv")
print(OUTPUT_DIR / "xgboost_metrics.csv")
print(OUTPUT_DIR / "best_heat_model.pkl")