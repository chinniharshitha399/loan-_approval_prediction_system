"""
utils/db.py — Database helpers shared across all page_modules
"""
import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text
import pandas as pd

# Always load from the project root .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path, override=True)


def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    pw   = os.getenv("DB_PASSWORD", "")
    db   = os.getenv("DB_NAME", "loan_approval_db")
    url  = f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"
    return sa.create_engine(url, pool_pre_ping=True)


def save_application(data: dict):
    """Save a loan application + prediction result to MySQL."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO loan_applications
                (person_age, person_income, person_home_ownership,
                 person_emp_length, loan_intent, loan_grade,
                 loan_amnt, loan_int_rate, loan_percent_income,
                 cb_person_default_on_file, cb_person_cred_hist_length,
                 prediction, probability)
                VALUES
                (:person_age, :person_income, :person_home_ownership,
                 :person_emp_length, :loan_intent, :loan_grade,
                 :loan_amnt, :loan_int_rate, :loan_percent_income,
                 :cb_person_default_on_file, :cb_person_cred_hist_length,
                 :prediction, :probability)
            """), data)
            conn.commit()
        return True
    except Exception as e:
        print(f"DB save error: {e}")
        return False


def get_all_applications():
    """Fetch all saved applications from MySQL."""
    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM loan_applications ORDER BY created_at DESC", engine)
        return df
    except Exception as e:
        print(f"DB fetch error: {e}")
        return pd.DataFrame()


def save_chat_message(role: str, message: str):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text(
                "INSERT INTO chat_history (role, message) VALUES (:role, :message)"
            ), {"role": role, "message": message})
            conn.commit()
    except Exception:
        pass


def get_model_metrics():
    try:
        engine = get_engine()
        df = pd.read_sql("SELECT * FROM model_metrics ORDER BY trained_at DESC", engine)
        return df
    except Exception:
        return pd.DataFrame()


def db_connected() -> bool:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
