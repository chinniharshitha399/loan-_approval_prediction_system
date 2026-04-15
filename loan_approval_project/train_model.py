"""
==============================================
MODEL TRAINING SCRIPT
Run this ONCE to train and save ML models.
It reads the CSV, trains 3 models, and saves
the best one as models/loan_model.pkl
==============================================
"""
import os
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)
from xgboost import XGBClassifier

load_dotenv()

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "credit_risk_dataset.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── DB helpers ───────────────────────────────────────────────────────────────
def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    pw   = os.getenv("DB_PASSWORD", "")
    db   = os.getenv("DB_NAME", "loan_approval_db")
    return sa.create_engine(f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}")


def save_metrics_to_db(name, acc, prec, rec, f1, auc):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO model_metrics
                (model_name, accuracy, precision_score, recall_score, f1_score, auc_roc)
                VALUES (:n, :a, :p, :r, :f, :u)
            """), {"n": name, "a": acc, "p": prec, "r": rec, "f": f1, "u": auc})
            conn.commit()
        print(f"   📊 Metrics saved to DB for {name}")
    except Exception as e:
        print(f"   ⚠️  DB not available, skipping metric save: {e}")


# ─── Main training function ────────────────────────────────────────────────────
def train_models():
    print("=" * 55)
    print("  LOAN APPROVAL AI — MODEL TRAINING")
    print("=" * 55)

    # ── Load data ──────────────────────────────────────────
    print("\n📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Rows: {len(df):,}  |  Columns: {df.shape[1]}")

    # ── Clean data ─────────────────────────────────────────
    print("\n🧹 Cleaning data...")
    df = df.dropna()

    # Remove unrealistic ages / employment length
    df = df[df["person_age"] < 100]
    df = df[df["person_emp_length"] < 60]

    print(f"   Clean rows: {len(df):,}")

    # ── Feature engineering ────────────────────────────────
    categorical_cols = [
        "person_home_ownership",
        "loan_intent",
        "loan_grade",
        "cb_person_default_on_file"
    ]

    le_dict = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le

    feature_cols = [
        "person_age", "person_income", "person_home_ownership",
        "person_emp_length", "loan_intent", "loan_grade",
        "loan_amnt", "loan_int_rate", "loan_percent_income",
        "cb_person_default_on_file", "cb_person_cred_hist_length"
    ]

    X = df[feature_cols]
    y = df["loan_status"]

    # ── Train/Test split ───────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ── Scale features ─────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # ── Define models ──────────────────────────────────────
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=15,
            min_samples_split=5, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            use_label_encoder=False, eval_metric="logloss",
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=5,
            learning_rate=0.1, random_state=42
        ),
    }

    # ── Train & evaluate ───────────────────────────────────
    print("\n🤖 Training models...")
    best_model_name = None
    best_auc        = 0
    best_model_obj  = None
    results         = {}

    for name, clf in models.items():
        print(f"\n   ▶ {name}...")
        if name == "Logistic Regression":
            clf.fit(X_train_s, y_train)
            preds = clf.predict(X_test_s)
            proba = clf.predict_proba(X_test_s)[:, 1]
        else:
            clf.fit(X_train, y_train)
            preds = clf.predict(X_test)
            proba = clf.predict_proba(X_test)[:, 1]

        acc  = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec  = recall_score(y_test, preds)
        f1   = f1_score(y_test, preds)
        auc  = roc_auc_score(y_test, proba)

        print(f"      Accuracy:  {acc:.4f}")
        print(f"      Precision: {prec:.4f}")
        print(f"      Recall:    {rec:.4f}")
        print(f"      F1:        {f1:.4f}")
        print(f"      AUC-ROC:   {auc:.4f}")

        results[name] = {"acc": acc, "prec": prec, "rec": rec, "f1": f1, "auc": auc}
        save_metrics_to_db(name, acc, prec, rec, f1, auc)

        if auc > best_auc:
            best_auc = auc
            best_model_name = name
            best_model_obj = clf

    # ── Save best model + artifacts ────────────────────────
    print(f"\n🏆 Best Model: {best_model_name}  (AUC={best_auc:.4f})")

    artifacts = {
        "model":          best_model_obj,
        "scaler":         scaler,
        "label_encoders": le_dict,
        "feature_cols":   feature_cols,
        "model_name":     best_model_name,
        "results":        results,
    }
    save_path = os.path.join(MODEL_DIR, "loan_model.pkl")
    joblib.dump(artifacts, save_path)
    print(f"   ✅ Model saved → {save_path}")

    # ── Feature importance (for RF / XGB) ─────────────────
    if hasattr(best_model_obj, "feature_importances_"):
        fi = pd.Series(
            best_model_obj.feature_importances_,
            index=feature_cols
        ).sort_values(ascending=False)
        fi.to_csv(os.path.join(MODEL_DIR, "feature_importance.csv"))
        print("   ✅ Feature importance saved")

    print("\n🎉 Training complete! Run  streamlit run app.py  to launch the app.")
    print("=" * 55)
    return artifacts


if __name__ == "__main__":
    train_models()
