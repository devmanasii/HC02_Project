
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------
# 1. File paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "heat_model_data_2023_2026.csv"
PREDICTIONS_FILE = DATA_DIR / "heat_model_predictions_2023_2026.csv"
METRICS_FILE = DATA_DIR / "heat_model_metrics_2023_2026.csv"

# --------------------------------------------------
# 2. Load and validate data
# --------------------------------------------------
df = pd.read_csv(INPUT_FILE)
df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
df = df.sort_values("Month").reset_index(drop=True)

target = "Total_AE_Attendances"

weather_features = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

required = ["Month", target] + weather_features
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

if df[required].isnull().any().any():
    raise ValueError("Missing values exist. Check the input dataset.")

# --------------------------------------------------
# 3. Create a chronological train/test split
#    Train: Jan 2023–Dec 2025
#    Test:  Jan 2026–Aug 2026
# --------------------------------------------------
train = df[df["Month"] < "2026-01-01"].copy()
test = df[df["Month"] >= "2026-01-01"].copy()

if len(train) < 12 or len(test) == 0:
    raise ValueError("Not enough data for the selected split.")

X_train = train[weather_features]
y_train = train[target]

X_test = test[weather_features]
y_test = test[target]

# --------------------------------------------------
# 4. Train weather-based regression model
# --------------------------------------------------
weather_model = make_pipeline(
    StandardScaler(),
    LinearRegression()
)

weather_model.fit(X_train, y_train)
weather_predictions = weather_model.predict(X_test)

# --------------------------------------------------
# 5. Previous-month baseline
#    Predict this month using the previous month's
#    actual attendance. This is a simple benchmark.
# --------------------------------------------------
previous_month_predictions = []

for month in test["Month"]:
    previous_month = month - pd.DateOffset(months=1)

    previous_rows = df.loc[
        df["Month"] == previous_month, target
    ]

    if previous_rows.empty:
        previous_month_predictions.append(np.nan)
    else:
        previous_month_predictions.append(
            float(previous_rows.iloc[0])
        )

# --------------------------------------------------
# 6. Calculate evaluation metrics
# --------------------------------------------------
def calculate_metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    return {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "MAPE_pct": np.mean(
            np.abs((actual - predicted) / actual)
        ) * 100,
    }

weather_metrics = calculate_metrics(
    y_test, weather_predictions
)

valid_baseline = ~np.isnan(previous_month_predictions)

baseline_metrics = calculate_metrics(
    y_test.to_numpy()[valid_baseline],
    np.asarray(previous_month_predictions)[valid_baseline],
)

# --------------------------------------------------
# 7. Save predictions
# --------------------------------------------------
predictions = test[["Month", target]].copy()
predictions["Weather_Model_Prediction"] = np.round(
    weather_predictions
)
predictions["Previous_Month_Baseline"] = (
    previous_month_predictions
)

predictions.to_csv(PREDICTIONS_FILE, index=False)

metrics = pd.DataFrame([
    {
        "Model": "Weather Linear Regression",
        "Train_Months": len(train),
        "Test_Months": len(test),
        **weather_metrics,
    },
    {
        "Model": "Previous-Month Baseline",
        "Train_Months": len(train),
        "Test_Months": int(valid_baseline.sum()),
        **baseline_metrics,
    },
])

metrics.to_csv(METRICS_FILE, index=False)

# --------------------------------------------------
# 8. Print results
# --------------------------------------------------
print("\nMODEL TRAINING AND EVALUATION COMPLETE")
print("Training period:",
      train["Month"].min().strftime("%Y-%m"),
      "to",
      train["Month"].max().strftime("%Y-%m"))
print("Training months:", len(train))

print("Testing period:",
      test["Month"].min().strftime("%Y-%m"),
      "to",
      test["Month"].max().strftime("%Y-%m"))
print("Testing months:", len(test))

print("\nEvaluation metrics:")
print(metrics.round(2).to_string(index=False))

print("\nTest predictions:")
print(predictions.to_string(index=False))

print("\nSaved predictions to:", PREDICTIONS_FILE)
print("Saved metrics to:", METRICS_FILE)