
import os
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# 2. Load the trained XGBoost model
# --------------------------------------------------

MODEL_PATH = (
    PROJECT_DIR
    / "outputs"
    / "verified_xgboost_model.pkl"
)

model = None
FEATURES = []

try:
    saved_data = joblib.load(MODEL_PATH)
    model = saved_data["model"]
    FEATURES = saved_data["features"]

    app.logger.info("XGBoost model loaded successfully.")

except FileNotFoundError:
    app.logger.exception("Model file not found: %s", MODEL_PATH)

except Exception:
    app.logger.exception("Could not load the XGBoost model.")

# --------------------------------------------------
# 3. Connect to Supabase
# --------------------------------------------------

supabase = None

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if supabase_url and supabase_key:
    try:
        supabase = create_client(
            supabase_url,
            supabase_key
        )
        app.logger.info("Supabase client initialized.")

    except Exception:
        app.logger.exception("Supabase initialization failed.")

else:
    app.logger.warning(
        "Supabase credentials are missing from .env."
    )

# --------------------------------------------------
# 4. Backend health check
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Backend is running",
        "model_loaded": model is not None,
        "supabase_configured": supabase is not None
    }), 200

# --------------------------------------------------
# 5. Fetch monthly attendance data from Supabase
# --------------------------------------------------

@app.route("/api/attendance", methods=["GET"])
def get_monthly_attendance():
    if supabase is None:
        return jsonify({
            "success": False,
            "error": "Supabase is not configured."
        }), 503

    try:
        response = (
            supabase
            .table("monthly_attendance")
            .select(
                "month,total_ae_attendances,provider_count,"
                "avg_max_temp_c,avg_min_temp_c,highest_temp_c,"
                "avg_humidity_pct,hot_days"
            )
            .order("month")
            .execute()
        )

        records = response.data or []

        return jsonify({
            "success": True,
            "count": len(records),
            "data": records
        }), 200

    except Exception:
        app.logger.exception(
            "Failed to fetch monthly attendance."
        )
        return jsonify({
            "success": False,
            "error": "Unable to fetch attendance data."
        }), 500

# --------------------------------------------------
# 6. Retrieve prediction history
# --------------------------------------------------

@app.route("/api/prediction-history", methods=["GET"])
def get_prediction_history():
    if supabase is None:
        return jsonify({
            "success": False,
            "error": "Supabase is not configured."
        }), 503

    try:
        response = (
            supabase
            .table("prediction_history")
            .select(
                "id,forecast_month,predicted_attendance,"
                "model_name,created_at"
            )
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        records = response.data or []

        return jsonify({
            "success": True,
            "count": len(records),
            "data": records
        }), 200

    except Exception:
        app.logger.exception(
            "Could not fetch prediction history."
        )
        return jsonify({
            "success": False,
            "error": "Unable to fetch prediction history."
        }), 500

# --------------------------------------------------
# 7. Save prediction history to Supabase
# --------------------------------------------------

@app.route("/api/prediction-history", methods=["POST"])
def save_prediction_history():
    if supabase is None:
        return jsonify({
            "success": False,
            "error": "Supabase is not configured."
        }), 503

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send inputs as a JSON object."
        }), 400

    try:
        attendance = float(data["predicted_attendance"])
        forecast_month = str(data["forecast_month"])

        if not np.isfinite(attendance) or attendance < 0:
            return jsonify({
                "error": "Predicted attendance must be non-negative."
            }), 400

        parsed_date = date.fromisoformat(forecast_month)

        if parsed_date.day != 1:
            return jsonify({
                "error": "Forecast date must be the first day of a month."
            }), 400

        response = (
            supabase
            .table("prediction_history")
            .insert({
                "forecast_month": parsed_date.isoformat(),
                "predicted_attendance": attendance,
                "model_name": "XGBoost"
            })
            .execute()
        )

        return jsonify({
            "success": True,
            "message": "Prediction saved successfully.",
            "data": response.data or []
        }), 201

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": (
                "Provide predicted_attendance and "
                "forecast_month in YYYY-MM-01 format."
            )
        }), 400

    except Exception:
        app.logger.exception(
            "Could not save prediction history."
        )
        return jsonify({
            "success": False,
            "error": "Unable to save prediction history."
        }), 500

# --------------------------------------------------
# 8. XGBoost prediction
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    if model is None or not FEATURES:
        return jsonify({
            "error": "The trained model is not available."
        }), 503

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Send inputs as a JSON object."
            }), 400

        values = []

        for feature in FEATURES:
            if feature not in data:
                return jsonify({
                    "error": f"Missing required input: {feature}"
                }), 400

            value = float(data[feature])

            if not np.isfinite(value):
                return jsonify({
                    "error": f"Invalid numeric value for {feature}."
                }), 400

            values.append(value)

        prediction = float(
            model.predict(
                np.array([values], dtype=float)
            )[0]
        )

        predicted_attendance = max(0, round(prediction))

        return jsonify({
            "predicted_attendance": predicted_attendance,
            "model": "XGBoost",
            "note": (
                "Preliminary estimate. Model accuracy "
                "requires further validation."
            )
        }), 200

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": (
                "Provide all required model inputs "
                "as valid numbers."
            )
        }), 400

    except Exception:
        app.logger.exception("Prediction failed.")
        return jsonify({
            "error": "Prediction failed."
        }), 500

# --------------------------------------------------
# 9. Current weather from OpenWeather
# --------------------------------------------------

@app.route("/weather", methods=["GET"])
def get_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return jsonify({
            "error": "Weather API key not found in .env."
        }), 503

    city = request.args.get("city", "Pune").strip()

    if not city:
        return jsonify({
            "error": "Provide a valid city name."
        }), 400

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": api_key,
                "units": "metric"
            },
            timeout=15
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Unable to fetch weather data.",
                "details": response.json().get(
                    "message",
                    "Weather API error"
                )
            }), response.status_code

        weather_data = response.json()

        return jsonify({
            "city": weather_data["name"],
            "temperature_c": weather_data["main"]["temp"],
            "humidity_pct": weather_data["main"]["humidity"],
            "weather": weather_data["weather"][0]["description"]
        }), 200

    except requests.RequestException:
        app.logger.exception(
            "Weather service request failed."
        )
        return jsonify({
            "error": "Weather service connection failed."
        }), 502

    except (KeyError, IndexError, TypeError):
        app.logger.exception(
            "Unexpected weather response."
        )
        return jsonify({
            "error": "Unexpected response from weather service."
        }), 502

# --------------------------------------------------
# 10. Start Flask server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
