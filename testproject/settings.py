import locale
import os

PROJECT = "djenealog"
PROJECT_VERBOSE = PROJECT.capitalize()

DOMAIN_NAME = os.environ.get("DOMAIN_NAME", "localhost")
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOST", f"{PROJECT}.{DOMAIN_NAME}")]
ALLOWED_HOSTS += [f"www.{host}" for host in ALLOWED_HOSTS]

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

INSTALLED_APPS = [
    PROJECT,
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django_bootstrap5",
    "ndh",
    "testproject",
    "django_tables2",
    "django_select2",
    "leaflet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "testproject.urls"

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

WSGI_APPLICATION = "testproject.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "postgres"),
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
    },
}

_APV = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": f"{_APV}.UserAttributeSimilarityValidator",
    },
    {
        "NAME": f"{_APV}.MinimumLengthValidator",
    },
    {
        "NAME": f"{_APV}.CommonPasswordValidator",
    },
    {
        "NAME": f"{_APV}.NumericPasswordValidator",
    },
]

locale.setlocale(locale.LC_ALL, "fr_FR.utf8")
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

SITE_ID = 1

MEDIA_ROOT = "/srv/media/"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
STATIC_ROOT = "/srv/static/"

if os.environ.get("REDIS", "False").lower() == "true":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://redis:6379",
        },
    }
DJANGO_TABLES2_TEMPLATE = f"{PROJECT}/tables.html"

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (43.5, 1.5),
    "DEFAULT_ZOOM": 8,
    "TILES": "http://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
}
