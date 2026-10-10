
import joblib

model = joblib.load("outputs/verified_xgboost_model.pkl")

print("Model loaded successfully!")

if hasattr(model, "feature_names_in_"):
    print("\nFeatures expected by the model:")
    for feature in model.feature_names_in_:
        print("-", feature)
else:
    print("\nFeature names are not stored in the model.")
    print("Check src/train_verified_models.py for the training feature list.")