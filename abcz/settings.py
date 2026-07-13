"""
Django settings for the ABCZ project.

Production target: Render or any WSGI host with Postgres, WhiteNoise, and
environment-driven security settings.
"""

from pathlib import Path
import os
import sys

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: str = "False") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default).strip()
    return [item.strip() for item in raw.split(",") if item.strip()]


ENVIRONMENT = os.getenv("DJANGO_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production" or env_bool("RENDER", "False")
DEBUG = env_bool("DEBUG", "False")
TESTING = "test" in sys.argv

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ImproperlyConfigured("SECRET_KEY must be set in production.")
    SECRET_KEY = "local-dev-secret-key-change-me-but-not-used-in-production-abc12345"

# Developer preview only. Never enable in production.
DEV_UNLOCK_VIP_BIRD = DEBUG and env_bool("DEV_UNLOCK_VIP_BIRD", "False")


# Hosts and CSRF
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS.extend(env_list("ALLOWED_HOSTS", "abcz-epbz.onrender.com"))
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "https://abcz-epbz.onrender.com")
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "phonics.apps.PhonicsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "phonics.middleware.RequestIDMiddleware",
    "phonics.middleware.RequestTimingMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "abcz.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "abcz.wsgi.application"


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DATABASES["default"]["CONN_MAX_AGE"] = int(os.getenv("DB_CONN_MAX_AGE", "60"))
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True


REDIS_URL = os.getenv("REDIS_URL", "").strip()
if IS_PRODUCTION and not REDIS_URL:
    raise ImproperlyConfigured("REDIS_URL must be configured in production for shared security rate limits.")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 3,
                "SOCKET_TIMEOUT": 3,
                "RETRY_ON_TIMEOUT": True,
                "IGNORE_EXCEPTIONS": False,
            },
            "KEY_PREFIX": os.getenv("CACHE_KEY_PREFIX", "abcz"),
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "abcz-local-cache",
            "TIMEOUT": 300,
        }
    }

SUBSCRIPTION_CACHE_TIMEOUT = 0 if TESTING else int(os.getenv("SUBSCRIPTION_CACHE_TIMEOUT", "300"))
STATIC_CONTENT_CACHE_TIMEOUT = 0 if TESTING else int(os.getenv("STATIC_CONTENT_CACHE_TIMEOUT", "1800"))
PUBLIC_PAGE_CACHE_TIMEOUT = int(os.getenv("PUBLIC_PAGE_CACHE_TIMEOUT", "600"))


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles")))
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))
STATICFILES_BACKEND = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if DEBUG or TESTING
    else "whitenoise.storage.CompressedManifestStaticFilesStorage"
)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": STATICFILES_BACKEND,
    },
}


# Production security
SECURE_SSL_REDIRECT = (not DEBUG) and (not TESTING) and env_bool("SECURE_SSL_REDIRECT", "True")
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_PROXY_SSL_HEADER = None if DEBUG else ("HTTP_X_FORWARDED_PROTO", "https")

RATE_LIMIT_LOGIN = int(os.getenv("RATE_LIMIT_LOGIN", "10"))
RATE_LIMIT_REGISTER = int(os.getenv("RATE_LIMIT_REGISTER", "5"))
RATE_LIMIT_WRITE = int(os.getenv("RATE_LIMIT_WRITE", "60"))
RATE_LIMIT_UPLOAD = int(os.getenv("RATE_LIMIT_UPLOAD", "10"))
RATE_LIMIT_PUBLIC_API = int(os.getenv("RATE_LIMIT_PUBLIC_API", "30"))

CSP_REPORT_ONLY = os.getenv(
    "CSP_REPORT_ONLY",
    "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
).strip()

if not DEBUG:
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True")
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", "True")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


DISABLE_AUTO_SEED = env_bool("DISABLE_AUTO_SEED", "False")
REQUEST_LOG_ENABLED = (not TESTING) and env_bool("REQUEST_LOG_ENABLED", "True")
ENABLE_SERVER_TIMING_HEADER = env_bool("ENABLE_SERVER_TIMING_HEADER", "False")


# Payment integration placeholders. Keep real secrets in environment variables only.
MOYASAR_ENABLED = env_bool("MOYASAR_ENABLED", "False")
MOYASAR_PUBLISHABLE_KEY = os.getenv("MOYASAR_PUBLISHABLE_KEY", "").strip()
MOYASAR_SECRET_KEY = os.getenv("MOYASAR_SECRET_KEY", "").strip()
MOYASAR_WEBHOOK_SECRET = os.getenv("MOYASAR_WEBHOOK_SECRET", "").strip()
MOYASAR_CALLBACK_URL = os.getenv("MOYASAR_CALLBACK_URL", "").strip()

BANK_TRANSFER_ENABLED = env_bool("BANK_TRANSFER_ENABLED", "True")
BANK_ACCOUNT_NAME = os.getenv("BANK_ACCOUNT_NAME", "").strip()
BANK_NAME = os.getenv("BANK_NAME", "").strip()
BANK_IBAN = os.getenv("BANK_IBAN", "").strip()
BANK_ACCOUNT_NUMBER = os.getenv("BANK_ACCOUNT_NUMBER", "").strip()
BANK_TRANSFER_INSTRUCTIONS = os.getenv("BANK_TRANSFER_INSTRUCTIONS", "").strip()


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "request": {
            "format": (
                "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s "
                "method=%(method)s path=%(path)s status=%(status_code)s duration_ms=%(duration_ms)s"
            )
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "request",
        },
    },
    "loggers": {
        "abcz.requests": {
            "handlers": ["console"],
            "level": os.getenv("REQUEST_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
