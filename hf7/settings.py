"""
Django settings for hf7 project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import io
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import environ
import google.auth
from google.cloud import secretmanager, storage

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = env("ENV_PATH", default=BASE_DIR / ".env")

if env_file.exists():
    env.read_env(str(env_file))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
TESTING = "test" in sys.argv


try:
    _, project_id = google.auth.default()

    client = secretmanager.SecretManagerServiceClient()
    settings_name = env("SETTINGS_NAME", default="hf-production")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"

    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    env.read_env(io.StringIO(payload))
except (
    google.auth.exceptions.DefaultCredentialsError,
    google.api_core.exceptions.NotFound,
    google.api_core.exceptions.PermissionDenied,
):
    pass

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG", default=False)

if not DEBUG:
    gcs = storage.Client()
    bucket = gcs.get_bucket("hf-private")
    blob = bucket.blob("prod-ca-2021.crt")
    blob.download_to_filename(os.path.join(BASE_DIR, "prod-ca-2021.crt"))


CURRENT_HOST = env.list("CURRENT_HOST", default=None)
if CURRENT_HOST:
    ALLOWED_HOSTS = [urlparse(host).netloc for host in CURRENT_HOST]
    CSRF_TRUSTED_ORIGINS = CURRENT_HOST
else:
    ALLOWED_HOSTS = ["localhost"]
    CSRF_TRUSTED_ORIGINS = ["http://localhost"]

if "localhost" not in ALLOWED_HOSTS:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "location_field.apps.DefaultConfig",
    "eventium.apps.EventiumConfig",
    "polium.apps.PoliumConfig",
    "spendium.apps.SpendiumConfig",
    "tasks.apps.TasksConfig",
    "utilities.apps.UtilitiesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "sesame.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hf7.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hf7.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if TESTING:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_URL"],
            "PORT": 6543,
            "OPTIONS": {
                "sslmode": "verify-full",
                "sslrootcert": os.path.join(BASE_DIR, "prod-ca-2021.crt"),
            },
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
GS_BUCKET_NAME = env("GS_BUCKET_NAME", default=None)

if GS_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_ACL = "publicRead"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# URL prepends
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# literal file locations
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.replace("/", ""))
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL.replace("/", ""))

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "utilities.HfUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

SESAME_MAX_AGE = 60 * 10  # in seconds
SESAME_SIGNATURE_SIZE = 14
SESAME_PACKER = "utilities.packers.Packer"
LOGIN_REDIRECT_URL = "/profile/"
CRISPY_TEMPLATE_PACK = "bootstrap"

if TESTING:
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

LOCATION_FIELD = {
    "map.provider": "mapbox",
    "provider.mapbox.access_token": os.environ.get("MAPBOX_TOKEN"),
    "provider.mapbox.id": "mapbox.streets",
}
