"""
==============================================
DATABASE SETUP SCRIPT
Run this ONCE before starting the Streamlit app.
It creates all necessary MySQL tables.
==============================================
"""
import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "loan_approval_db")


def get_engine(with_db=True):
    if with_db:
        url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    return sa.create_engine(url)


def setup_database():
    print("=" * 50)
    print("  LOAN APPROVAL DB SETUP")
    print("=" * 50)

    # Step 1: Create database
    engine_no_db = get_engine(with_db=False)
    with engine_no_db.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        print(f"✅ Database '{DB_NAME}' created/verified.")

    # Step 2: Create tables
    engine = get_engine(with_db=True)
    with engine.connect() as conn:

        # Table: loan_applications (stores every prediction)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS loan_applications (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                person_age      INT,
                person_income   INT,
                person_home_ownership VARCHAR(20),
                person_emp_length FLOAT,
                loan_intent     VARCHAR(50),
                loan_grade      VARCHAR(5),
                loan_amnt       INT,
                loan_int_rate   FLOAT,
                loan_percent_income FLOAT,
                cb_person_default_on_file VARCHAR(5),
                cb_person_cred_hist_length INT,
                prediction      VARCHAR(20),
                probability     FLOAT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Table 'loan_applications' created/verified.")

        # Table: chat_history (stores chatbot conversations)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                role        VARCHAR(20),
                message     TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Table 'chat_history' created/verified.")

        # Table: model_metrics (stores model performance logs)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                model_name  VARCHAR(50),
                accuracy    FLOAT,
                precision_score FLOAT,
                recall_score    FLOAT,
                f1_score        FLOAT,
                auc_roc         FLOAT,
                trained_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Table 'model_metrics' created/verified.")
        conn.commit()

    print("\n🎉 Database setup complete! You can now run: streamlit run app.py")
    print("=" * 50)


if __name__ == "__main__":
    try:
        setup_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. MySQL Workbench is running")
        print("  2. Your .env file has correct DB_PASSWORD")
        print("  3. MySQL service is started")
