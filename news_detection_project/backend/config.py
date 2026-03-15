import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

FAKE_CSV_PATH = DATA_DIR / "Fake.csv"
TRUE_CSV_PATH = DATA_DIR / "True.csv"

MODEL_PATH = MODELS_DIR / "news_detection_model.pkl"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "localhost")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

MODEL_CONFIG = {
    "max_features": 5000,
    "stop_words": "english",
    "min_df": 5,
    "max_df": 0.7,
    "test_size": 0.2,
    "random_state": 42,
    "max_iter": 1000,
    "solver": "lbfgs"
}

TEXT_CLEANING = {
    "lowercase": True,
    "remove_special_chars": True,
    "pattern": r"[^a-zA-Z ]"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "console": True,
        "file": True,
        "file_path": LOGS_DIR / "app.log"
    }
}

# CORS Configuration (for frontend access)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8501",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
]

# Security
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_TYPES = [".csv", ".txt"]

def get_config():
    """Get current configuration"""
    return {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "models_dir": str(MODELS_DIR),
        "api_url": f"http://{API_HOST}:{API_PORT}",
        "model_config": MODEL_CONFIG
    }

if __name__ == "__main__":
    import json
    config = get_config()
    print(json.dumps(config, indent=2))
