"""
Django settings for palestinement project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = env.path("LOG_DIR", default=Path.joinpath(BASE_DIR, "logs"))  # type: ignore

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY")  # type: ignore

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # type: ignore


# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = DJANGO_APPS + [
    "corsheaders",
    "rest_framework",
    "knox",
    "apps.listings.Config",
    "apps.orders.Config",
    "apps.users.Config",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [  # type: ignore
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "json_log_formatter.JSONFormatter",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": f"{LOG_DIR}/debug.log",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

WSGI_APPLICATION = "settings.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# postgres DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("apps.users.auth.CookieTokenAuthentication",),
    # "DEFAULT_PERMISSION_CLASSES": ("services.security.permissions.Deny",),
}

REST_KNOX = {
    "USER_SERIALIZER": "apps.users.serializers.ClientSerializer",
}

CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_ALLOWED_ORIGINS", default=["http://localhost:8000", "http://127.0.0.1:8000"]
)  # type: ignore

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "users.Client"

AUTH_PASSWORD_VALIDATORS = (
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
)

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
