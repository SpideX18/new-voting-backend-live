from pathlib import Path
import os
from decouple import config
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config("SECRET_KEY")
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.onrender.com').split(',')

# Apps
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'cloudinary_storage',  # BEFORE staticfiles
    'cloudinary',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'elections',
    'rest_framework.authtoken',
    'users',
    'corsheaders',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://192.168.18.61:8081",
    "http://10.10.8.138:8081",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'voting_backend.urls'

# Templates
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

WSGI_APPLICATION = 'voting_backend.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}

AUTH_USER_MODEL = 'users.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# i18n
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CLOUDINARY CONFIG - FIXED
# ============================================

# Option 1: Hardcoded (works but not recommended for security)
cloudinary.config(
    cloud_name='dojpkrc1q',
    api_key='929397431423256',
    api_secret='9-PkTAcD0p6yhTAz9tTFvnnl_lQ',
    secure=True
)

# Option 2: From env vars (BETTER - uncomment and use this instead)
# cloudinary.config(
#     cloud_name=config('CLOUDINARY_CLOUD_NAME', default='dojpkrc1q'),
#     api_key=config('CLOUDINARY_API_KEY', default='929397431423256'),
#     api_secret=config('CLOUDINARY_API_SECRET', default='9-PkTAcD0p6yhTAz9tTFvnnl_lQ'),
#     secure=True
# )

# Tell Django to use Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'