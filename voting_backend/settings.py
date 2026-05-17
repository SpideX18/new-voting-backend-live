from pathlib import Path
import os
from decouple import config
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api


MEDIA_URL = '/media/'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Quick-start development settings - unsuitable for production
SECRET_KEY = config("SECRET_KEY")

DEBUG = config('DEBUG',default=False,cast=bool)

# Allow your local network IP and localhost for mobile access
# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.100']  # <-- Replace with your PC IP
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.onrender.com').split(',')# Application definition
INSTALLED_APPS = [
        'whitenoise.runserver_nostatic',   # add at top of list
    'django.contrib.admin',
    'django.contrib.auth',
    'cloudinary_storage',  
    'cloudinary',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'elections',
    'rest_framework.authtoken',
    'users',
    'corsheaders',  # Must be here for CORS
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first for CORS
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


# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For testing only, allow all origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    
    "http://192.168.18.61:8081",
    "http://10.10.8.138:8081",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'voting_backend.urls'

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

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'users.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


cloudinary.config(
    cloud_name=config('dojpkrc1q', default=''),
    api_key=config('929397431423256', default=''),
    api_secret=config('9-PkTAcD0p6yhTAz9tTFvnnl_lQ', default=''),
    secure=True
)

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'