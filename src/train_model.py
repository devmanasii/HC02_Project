
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.dummy import DummyRegressor

from xgboost import XGBRegressor


# ==========================================================
# 1. PROJECT SETTINGS
# ==========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "heat_model_data_verified.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"

TARGET_COLUMN = "Total_AE_Attendances"
DATE_COLUMN = "Month"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# 2. LOAD AND VALIDATE DATA
# ==========================================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Check the DATA_PATH setting."
    )

df = pd.read_csv(DATA_PATH)

required_columns = [TARGET_COLUMN, DATE_COLUMN]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found.\n"
            f"Available columns: {df.columns.tolist()}"
        )

df[DATE_COLUMN] = pd.to_datetime(
    df[DATE_COLUMN],
    errors="coerce"
)

df[TARGET_COLUMN] = pd.to_numeric(
    df[TARGET_COLUMN],
    errors="coerce"
)

df = df.dropna(
    subset=[DATE_COLUMN, TARGET_COLUMN]
).copy()

df = df.sort_values(DATE_COLUMN).reset_index(drop=True)

if df[DATE_COLUMN].duplicated().any():
    raise ValueError(
        "Duplicate months found. Resolve them before training."
    )

if len(df) < 15:
    raise ValueError(
        "Too few monthly records for this training setup."
    )

print("\nDataset loaded successfully.")
print(f"Dataset: {DATA_PATH.name}")
print(f"Number of records: {len(df)}")
print(f"Date range: {df[DATE_COLUMN].min()} to "
      f"{df[DATE_COLUMN].max()}")


# ==========================================================
# 3. CREATE CALENDAR AND LAG FEATURES
# ==========================================================

df["year"] = df[DATE_COLUMN].dt.year
df["month"] = df[DATE_COLUMN].dt.month

# Cyclical features help represent the repeating yearly pattern.
df["month_sin"] = np.sin(
    2 * np.pi * df["month"] / 12
)
df["month_cos"] = np.cos(
    2 * np.pi * df["month"] / 12
)

# Previous-month and previous-two-month attendance.
df["attendance_lag_1"] = df[TARGET_COLUMN].shift(1)
df["attendance_lag_2"] = df[TARGET_COLUMN].shift(2)

# Previous-month weather, which is known by the forecast date.
weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

for column in weather_columns:
    if column in df.columns:
        df[f"{column}_lag_1"] = df[column].shift(1)

# Do not use the current month's weather to predict its attendance.
# Exclude the original date and target from the input features.
df = df.dropna(
    subset=["attendance_lag_1", "attendance_lag_2"]
).reset_index(drop=True)

if len(df) < 12:
    raise ValueError(
        "Too few records remain after creating lag features."
    )


# ==========================================================
# 4. PREPARE INPUTS AND TARGET
# ==========================================================

excluded_columns = [DATE_COLUMN, TARGET_COLUMN]

X = df.drop(columns=excluded_columns)

# Avoid using actual weather from the month being predicted.
current_weather_columns = [
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

X = X.drop(
    columns=[
        col for col in current_weather_columns
        if col in X.columns
    ],
    errors="ignore",
)
y = df[TARGET_COLUMN]

# Remove columns that have no usable values.
X = X.dropna(axis=1, how="all")

if X.shape[1] == 0:
    raise ValueError("No usable input features remain.")

numeric_columns = X.select_dtypes(
    include=np.number
).columns.tolist()

categorical_columns = X.select_dtypes(
    exclude=np.number
).columns.tolist()

print("\nFeatures used:")
for column in X.columns:
    print(f"- {column}")


# ==========================================================
# 5. CHRONOLOGICAL TRAIN/TEST SPLIT
# ==========================================================

# Earlier months train the model; later months test it.
split_index = int(len(X) * 0.8)

if split_index <= 0 or split_index >= len(X):
    raise ValueError("Cannot create the 80/20 split.")

X_train = X.iloc[:split_index].copy()
X_test = X.iloc[split_index:].copy()

y_train = y.iloc[:split_index].copy()
y_test = y.iloc[split_index:].copy()

print("\nTraining/testing split:")
print(f"Training records: {len(X_train)}")
print(f"Testing records:  {len(X_test)}")
print(f"First test month: {df[DATE_COLUMN].iloc[split_index]}")


# ==========================================================
# 6. PREPROCESSING
# ==========================================================

transformers = []

if numeric_columns:
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median"))
    ])

    transformers.append((
        "numeric",
        numeric_pipeline,
        numeric_columns
    ))

if categorical_columns:
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    transformers.append((
        "categorical",
        categorical_pipeline,
        categorical_columns
    ))

preprocessor = ColumnTransformer(
    transformers=transformers
)


# ==========================================================
# 7. DEFINE MODELS
# ==========================================================

models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBRegressor(
        n_estimators=100,
        max_depth=2,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=5,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    ),
}


# ==========================================================
# 8. BASELINE AND MODEL TRAINING
# ==========================================================

results = []
trained_models = {}
prediction_results = {}

# Baseline: predict the average attendance from training months.
baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)

baseline_predictions = baseline.predict(X_test)

results.append({
    "Model": "Mean Baseline",
    "MAE": mean_absolute_error(
        y_test, baseline_predictions
    ),
    "RMSE": np.sqrt(
        mean_squared_error(y_test, baseline_predictions)
    ),
    "R2": (
        r2_score(y_test, baseline_predictions)
        if len(y_test) >= 2 else np.nan
    )
})

prediction_results["Mean Baseline"] = baseline_predictions

for name, model in models.items():
    print(f"\nTraining {name}...")

    pipeline = Pipeline([
        ("preprocessing", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )
    r2 = (
        r2_score(y_test, predictions)
        if len(y_test) >= 2 else np.nan
    )

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    trained_models[name] = pipeline
    prediction_results[name] = predictions

    print(f"MAE:  {mae:,.2f}")
    print(f"RMSE: {rmse:,.2f}")
    print(f"R2:   {r2:.3f}")


# ==========================================================
# 9. COMPARE MODELS
# ==========================================================

comparison = pd.DataFrame(results).sort_values(
    "MAE"
).reset_index(drop=True)

comparison_path = OUTPUT_DIR / "model_comparison.csv"
comparison.to_csv(comparison_path, index=False)

print("\nModel comparison (lower MAE is better):")
print(comparison.to_string(index=False))

# Save predictions for inspection.
prediction_table = pd.DataFrame({
    "Month": df[DATE_COLUMN].iloc[split_index:].values,
    "Actual_Attendance": y_test.values,
})

for name, predictions in prediction_results.items():
    safe_name = name.replace(" ", "_")
    prediction_table[f"{safe_name}_Prediction"] = predictions

prediction_path = OUTPUT_DIR / "test_predictions.csv"
prediction_table.to_csv(prediction_path, index=False)


# ==========================================================
# 10. SAVE THE BEST ML MODEL
# ==========================================================

# Save a deployable ML model only if it beats the baseline.
baseline_mae = comparison.loc[
    comparison["Model"] == "Mean Baseline", "MAE"
].iloc[0]

ml_results = comparison[
    comparison["Model"].isin(trained_models.keys())
]

best_ml_name = ml_results.iloc[0]["Model"]
best_ml_mae = ml_results.iloc[0]["MAE"]

if best_ml_mae < baseline_mae:
    best_pipeline = trained_models[best_ml_name]

    model_path = OUTPUT_DIR / "best_model.pkl"
    joblib.dump(best_pipeline, model_path)

    print(f"\nBest ML model: {best_ml_name}")
    print(f"Saved model: {model_path}")
else:
    print(
        "\nWARNING: Neither ML model beat the mean baseline "
        "on this test split."
    )
    print(
        "No new best_model.pkl was saved. Do not claim that "
        "an ML model is better until it passes evaluation."
    )


# ==========================================================
# 11. SAVE FEATURE INFORMATION AND FINISH
# ==========================================================

feature_path = OUTPUT_DIR / "model_features.txt"

with open(feature_path, "w", encoding="utf-8") as file:
    file.write("HEATCARE model input features\n")
    file.write("\n".join(X.columns.tolist()))
    file.write("\n\nTarget column:\n")
    file.write(TARGET_COLUMN)

print("\nFiles generated:")
print(f"- {comparison_path}")
print(f"- {prediction_path}")
print(f"- {feature_path}")
print("\nTraining and evaluation finished.")