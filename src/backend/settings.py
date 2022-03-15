"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import hashlib
from pathlib import Path
import json
from jwcrypto import jwt, jwk
import random
import string

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

SETTINGS_JSON = "settings.json"
INTERN_SETTINGS = {
    "email_address": "",
    "email_password": "",
    "email_smtp_server": "",
    "admin_username": "admin",
    "admin_password": "admin",
    "trainer_username": "trainer",
    "trainer_password": "trainer",
    "user_username": "user",
    "user_password": "user",
    "database": {
        "name": "bpws",
        "user": "admin",
        "password": "",
        "host": "localhost",
    },
    "video_dir": "videos/",
    "secret_key": get_random_string(16),
    "allowed_origins": ["http://localhost:80", "http://localhost:81"],
    "website_url": "https://my_url.de",
    "last_leaderboard_reset": 0
}
try:
    with open(SETTINGS_JSON) as json_file:
        INTERN_SETTINGS = json.load(json_file)
except:
    json.dump(INTERN_SETTINGS, open(SETTINGS_JSON, "w"), indent=4)
    print("Please enter settings at: ", SETTINGS_JSON)
    exit()

try:
    TOKEN_KEY = INTERN_SETTINGS["token_key"]
except:
    key = jwk.JWK(generate='oct', size=256)
    ## token in settings.json speichern
    newSetting = INTERN_SETTINGS
    newSetting["token_key"] = key
    json.dump(newSetting, open(SETTINGS_JSON, "w"), indent=4)
    


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = INTERN_SETTINGS["secret_key"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['78.46.150.116', '127.0.0.1']

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    "Session-Token",
]

CORS_ALLOWED_ORIGINS = INTERN_SETTINGS["allowed_origins"]

# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend',
    'corsheaders',
    'ordered_model',
    'rest_framework'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': INTERN_SETTINGS["database"]["name"],
        'USER': INTERN_SETTINGS["database"]["user"],
        'PASSWORD': INTERN_SETTINGS["database"]["password"],
        'HOST': INTERN_SETTINGS["database"]["host"],
        'POST': '',
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = INTERN_SETTINGS["email_smtp_server"]
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = INTERN_SETTINGS["email_address"]
EMAIL_HOST_PASSWORD = INTERN_SETTINGS["email_password"]
