"""
utils/model.py — Load trained model and run predictions
"""
import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "loan_model.pkl")


def load_model():
    """Load the saved model artifacts. Returns dict or None."""
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict(input_dict: dict, artifacts: dict):
    """
    Run prediction on a single applicant.

    Parameters
    ----------
    input_dict : dict with raw (un-encoded) feature values
    artifacts  : dict returned by load_model()

    Returns
    -------
    prediction : str  — 'Approved' or 'Rejected'
    probability: float — probability of approval (class 1)
    """
    model         = artifacts["model"]
    scaler        = artifacts["scaler"]
    le_dict       = artifacts["label_encoders"]
    feature_cols  = artifacts["feature_cols"]
    model_name    = artifacts["model_name"]

    # Build a one-row dataframe
    row = {}
    categorical_cols = [
        "person_home_ownership", "loan_intent",
        "loan_grade", "cb_person_default_on_file"
    ]

    for col in feature_cols:
        if col in categorical_cols:
            le = le_dict[col]
            val = input_dict[col]
            row[col] = le.transform([val])[0]
        else:
            row[col] = input_dict[col]

    X = pd.DataFrame([row])[feature_cols]

    # Logistic Regression needs scaling; others don't
    if model_name == "Logistic Regression":
        X_input = scaler.transform(X)
    else:
        X_input = X.values

    pred  = model.predict(X_input)[0]
    proba = model.predict_proba(X_input)[0][1]

    label = "Approved" if pred == 0 else "Rejected"
    return label, float(proba)
