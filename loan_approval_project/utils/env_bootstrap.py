"""
Load .env from fixed paths so GROQ_API_KEY and DB_* work even when Streamlit's
current working directory is not the project folder.
"""
import os
from dotenv import load_dotenv


def load_project_env():
    """Load `.env` from the app root and optionally the parent directory."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for rel in (".env", os.path.join("..", ".env")):
        path = os.path.abspath(os.path.join(root, rel))
        if os.path.isfile(path):
            load_dotenv(path, override=True)
