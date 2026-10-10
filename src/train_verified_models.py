
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "heat_model_data_rebuilt.csv"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_FILE)
df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")

df = df.sort_values("Month").reset_index(drop=True)

# Calendar features
df["Month_Number"] = df["Month"].dt.month
df["Month_Sin"] = np.sin(2 * np.pi * df["Month_Number"] / 12)
df["Month_Cos"] = np.cos(2 * np.pi * df["Month_Number"] / 12)

# Previous month's attendance
df["Previous_Month_Attendance"] = df["Total_AE_Attendances"].shift(1)
df = df.dropna().reset_index(drop=True)

features = [
    "Previous_Month_Attendance",
    "Month_Sin",
    "Month_Cos",
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

X = df[features]
y = df["Total_AE_Attendances"]

# Chronological split: train on earlier months, test on later months
split = int(len(df) * 0.75)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]
test_months = df["Month"].iloc[split:]

models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        min_samples_leaf=2,
        random_state=42,
    ),
    "XGBoost": XGBRegressor(
        n_estimators=100,
        max_depth=2,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
    ),
}

results = []
prediction_data = pd.DataFrame({
    "Month": test_months.dt.strftime("%Y-%m").to_numpy(),
    "Actual_Attendance": y_test.to_numpy(),
})

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mape = np.mean(
        np.abs((y_test.to_numpy() - predictions) / y_test.to_numpy())
    ) * 100

    results.append({
        "Model": name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE_Percent": round(mape, 2),
    })

    prediction_data[name.replace(" ", "_") + "_Prediction"] = np.round(
        predictions
    )

    print(f"\n{name}")
    print(f"MAE:  {mae:,.2f}")
    print(f"RMSE: {rmse:,.2f}")
    print(f"MAPE: {mape:.2f}%")

    if name == "XGBoost":
        joblib.dump(
            {"model": model, "features": features},
            OUTPUT_DIR / "verified_xgboost_model.pkl",
        )

# Simple baseline: predict this month's attendance using last month's value
baseline_predictions = X_test["Previous_Month_Attendance"].to_numpy()

baseline_mae = mean_absolute_error(y_test, baseline_predictions)
baseline_rmse = np.sqrt(
    mean_squared_error(y_test, baseline_predictions)
)
baseline_mape = np.mean(
    np.abs((y_test.to_numpy() - baseline_predictions) / y_test.to_numpy())
) * 100

results.append({
    "Model": "Previous-Month Baseline",
    "MAE": round(baseline_mae, 2),
    "RMSE": round(baseline_rmse, 2),
    "MAPE_Percent": round(baseline_mape, 2),
})

prediction_data["Baseline_Prediction"] = np.round(baseline_predictions)

metrics = pd.DataFrame(results).sort_values("MAE")
metrics.to_csv(OUTPUT_DIR / "verified_model_comparison.csv", index=False)
prediction_data.to_csv(
    OUTPUT_DIR / "verified_model_predictions.csv", index=False
)

print("\n=== MODEL COMPARISON (lower is better) ===")
print(metrics.to_string(index=False))
print("\nSaved comparison:", OUTPUT_DIR / "verified_model_comparison.csv")
print("Saved predictions:", OUTPUT_DIR / "verified_model_predictions.csv")