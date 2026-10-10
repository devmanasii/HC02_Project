
import joblib
import numpy as np
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "outputs" / "verified_xgboost_model.pkl"

model = joblib.load(MODEL_PATH)

FEATURES = [
    "Previous_Month_Attendance",
    "Month_Sin",
    "Month_Cos",
    "Avg_Max_Temp_C",
    "Avg_Min_Temp_C",
    "Highest_Temp_C",
    "Avg_Humidity_Pct",
    "Hot_Days",
]

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend is running"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Please send inputs as JSON."}), 400

        values = []

        for feature in FEATURES:
            value = float(data[feature])

            if not np.isfinite(value):
                return jsonify({
                    "error": f"{feature} must be a valid number."
                }), 400

            values.append(value)

        # Preserve the feature order used during model training.
        inputs = np.array([values], dtype=float)
        prediction = float(model.predict(inputs)[0])

        return jsonify({
            "predicted_attendance": max(0, round(prediction)),
            "note": (
                "Preliminary model estimate; "
                "not a validated emergency alert."
            )
        })

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "Please provide all eight inputs as valid numbers."
        }), 400
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "Prediction failed. Check the terminal for details."
        }), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)