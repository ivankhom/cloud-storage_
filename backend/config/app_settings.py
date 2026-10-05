"""Параметры окружения (БД, хранилище, ключи), вынесенные из settings.py."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(value, default=False):
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


SECRET_KEY = os.environ.get("APP_SECRET_KEY", "django-insecure-CHANGE-ME-IN-PRODUCTION")
DEBUG = _bool(os.environ.get("APP_DEBUG"), default=True)
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("APP_ALLOWED_HOSTS", "*").split(",") if h.strip()]

USE_SQLITE = _bool(os.environ.get("APP_USE_SQLITE"), default=False)

DB_NAME = os.environ.get("APP_DB_NAME", "cloud_storage")
DB_USER = os.environ.get("APP_DB_USER", "cloud_storage_user")
DB_PASSWORD = os.environ.get("APP_DB_PASSWORD", "cloud_storage_password")
DB_HOST = os.environ.get("APP_DB_HOST", "127.0.0.1")
DB_PORT = os.environ.get("APP_DB_PORT", "5432")

STORAGE_ROOT = Path(os.environ.get("APP_STORAGE_ROOT", BASE_DIR / "storage_data"))
MAX_UPLOAD_SIZE = int(os.environ.get("APP_MAX_UPLOAD_SIZE", 200 * 1024 * 1024))

DEFAULT_ADMIN_LOGIN = os.environ.get("APP_ADMIN_LOGIN", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("APP_ADMIN_PASSWORD", "Admin123!")
DEFAULT_ADMIN_EMAIL = os.environ.get("APP_ADMIN_EMAIL", "admin@example.com")

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("APP_CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("APP_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
SECURE_COOKIES = _bool(os.environ.get("APP_SECURE_COOKIES"), default=False)
