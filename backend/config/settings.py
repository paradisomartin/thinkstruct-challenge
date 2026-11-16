"""Minimal ingestion settings; no HTTP server or authentication configured yet."""

import os


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
INSTALLED_APPS = ["patents"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "thinkstruct"),
        "USER": os.environ.get("POSTGRES_USER", "thinkstruct"),
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
