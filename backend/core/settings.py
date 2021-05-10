"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from os import getenv
import requests

PROD = True if getenv("MODE").lower() == "prod" else False
ELASTICSEARCH_ENABLED = (
    True if getenv("ELASTICSEARCH_ENABLED").lower() == "true" else False
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if PROD else True

if PROD:
    ALLOWED_HOSTS = [f".{getenv('SITE_DOMAIN')}"]

    # Get IP address of load balancer to allow load balancer health checks
    ecs_metadata_endpoint = getenv("ECS_CONTAINER_METADATA_URI_V4")
    r = requests.get(ecs_metadata_endpoint)
    r.raise_for_status
    for network in r.json()["Networks"]:
        if network["NetworkMode"] == "awsvpc":
            ALLOWED_HOSTS.extend(network["IPv4Addresses"])
else:
    ALLOWED_HOSTS = ["django", "localhost"]

# Elastic Search
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html
ELASTICSEARCH_DSL = {
    "default": {"hosts": f"{getenv('ES_HOST')}:{getenv('ES_PORT')}"},
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "ctgov",
    "corsheaders",
    "health_check",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    "debug_toolbar",
    "logging_endpoint",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_CREDENTIALS = True

# Whitelist the dev frontend
if not PROD:
    CORS_ORIGIN_WHITELIST = ["http://localhost:3000"]

ROOT_URLCONF = "core.urls"

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "1000/day"},
}

TEMPLATES = [
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

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "aact",
        "USER": "postgres",
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST"),
        "PORT": getenv("DB_PORT"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"


# New in Django 3.2, customize type of auto-created primary keys
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["django_log_handler"]},
    "handlers": {
        "django_log_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "var/log/django.log",
            "formatter": "app",
        },
        "react_log_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "var/log/react.log",
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_log_handler"],
            "level": "INFO",
            "propagate": True,
        },
        "react": {
            "handlers": ["react_log_handler"],
            "level": "INFO",
            "propagate": True,
        },
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            )
        },
    },
}

# For frontend logging
LOGGING_ENDPOINT_LOGGER = "react"

if not PROD:
    # Required for django debug toolbar
    INTERNAL_IPS = ["127.0.0.1"]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }

    DEBUG_TOOLBAR_PANELS = [
        "ddt_request_history.panels.request_history.RequestHistoryPanel",  # Here it is
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
