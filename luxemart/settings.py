from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "channels",
    "apps.accounts",
    "apps.catalog",
    "apps.cart",
    "apps.orders",
    "apps.payments",
    "apps.dashboard",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "luxemart.urls"

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
                "django.template.context_processors.media",
            ],
        },
    },
]

ASGI_APPLICATION = "luxemart.asgi.application"
WSGI_APPLICATION = "luxemart.wsgi.application"

DEFAULT_DATABASE_URL = "postgres://postgres:password@localhost:5432/luxemart"

DATABASES = {
    "default": env.db("DATABASE_URL", default=DEFAULT_DATABASE_URL)
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default file storage for user-uploaded media (local filesystem)
STORAGES["default"] = {
    "BACKEND": "django.core.files.storage.FileSystemStorage",
    "OPTIONS": {"location": str(BASE_DIR / "media")},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

AUTHENTICATION_BACKENDS = [
    "apps.accounts.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
