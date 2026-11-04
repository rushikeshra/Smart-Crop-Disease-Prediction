import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    # Flask Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "smart_crop_default_secret_key_2026")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "smart_crop_db")

    # SQLAlchemy Database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads & Storage
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size

    # ML Inference Settings
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.60"))
    IMAGE_SIZE = (224, 224)
    _model_path = os.getenv("MODEL_PATH", os.path.join("models", "disease_model.keras"))
    MODEL_PATH = _model_path if os.path.isabs(_model_path) else os.path.join(BASE_DIR, _model_path)
    _class_names_path = os.getenv("CLASS_NAMES_PATH", os.path.join("models", "class_names.json"))
    CLASS_NAMES_PATH = _class_names_path if os.path.isabs(_class_names_path) else os.path.join(BASE_DIR, _class_names_path)
    _disease_info_path = os.getenv("DISEASE_INFO_PATH", os.path.join("database", "disease_info.json"))
    DISEASE_INFO_PATH = _disease_info_path if os.path.isabs(_disease_info_path) else os.path.join(BASE_DIR, _disease_info_path)
