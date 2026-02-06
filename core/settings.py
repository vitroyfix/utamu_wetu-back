"""
Django settings for core project.
Optimized for Utamu Wetu - Supabase & Cloudinary & Render Ready.
"""
import os
import sys
from pathlib import Path
import dj_database_url
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent

# Adds 'apps' folder to path for cleaner imports
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# --- SECURITY ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-for-dev-only')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Required for Render HTTPS/CSRF protection
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# --- APPS ---
INSTALLED_APPS = [
    'cloudinary_storage', # CRITICAL: Must be above staticfiles
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'corsheaders',
    'cloudinary',
    'apps.store',
    'apps.users',
    'apps.orders'
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Top priority
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files after security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
# core/settings.py

# core/settings.py

# --- DATABASE CONFIGURATION (Render/Supabase & Docker Compatible) ---
# This configuration handles seamless transitions between:
# - Local Docker (db service, no SSL)
# - Render/Supabase (remote host, SSL required)

db_url = os.environ.get('DATABASE_URL', '').strip()

if db_url:
    # Parse the DATABASE_URL for production/docker environments
    parsed_db = dj_database_url.config(default=db_url, conn_max_age=600)
    
    # Determine SSL requirement based on environment
    # Local/Docker environments don't require SSL
    is_local_or_docker = any(host in db_url for host in ['db', '127.0.0.1', 'localhost'])
    if is_local_or_docker:
        # Remove SSL for local development
        parsed_db['OPTIONS'] = parsed_db.get('OPTIONS', {})
        parsed_db['OPTIONS'].pop('sslmode', None)
        parsed_db['OPTIONS']['sslmode'] = 'disable'
    else:
        # Enforce SSL for Render/Supabase in production
        parsed_db['OPTIONS'] = parsed_db.get('OPTIONS', {})
        parsed_db['OPTIONS']['sslmode'] = 'require'
    
    DATABASES = {'default': parsed_db}
else:
    # Fallback for development without DATABASE_URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DATABASE_NAME', 'utamu_db'),
            'USER': os.environ.get('DATABASE_USER', 'postgres'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
            'HOST': os.environ.get('DATABASE_HOST', 'db'),
            'PORT': os.environ.get('DATABASE_PORT', '5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {'sslmode': 'disable'},
        }
    }
# --- STATIC & MEDIA FILES (Django 4.2+ with Render & Cloudinary Support) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure staticfiles directory exists BEFORE any collectstatic operations
os.makedirs(STATIC_ROOT, exist_ok=True)

# Cloudinary Config (Used by cloudinary_storage)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Determine which storage backend to use based on Cloudinary availability
HAS_CLOUDINARY = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))

# WhiteNoise Configuration for Production/Render
# Use CompressedStaticFilesStorage with proper settings
# WHITENOISE_MANIFEST_STRICT = False prevents errors on missing files
WHITENOISE_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Django 4.2+ STORAGES API (New Standard)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"
        if HAS_CLOUDINARY
        else "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {} if HAS_CLOUDINARY else {"location": os.path.join(BASE_DIR, 'media')},
    },
    "staticfiles": {
        "BACKEND": WHITENOISE_STORAGE,
    },
}

# Backward Compatibility: cloudinary_storage library expects STATICFILES_STORAGE
# This prevents AttributeError in third-party packages using the old API
STATICFILES_STORAGE = WHITENOISE_STORAGE

# WhiteNoise Configuration for Production/Render
# WHITENOISE_MANIFEST_STRICT = False allows missing admin files that may not exist
# WHITENOISE_USE_GZIP = True reduces file size for production (gzip already serves faster than brotli)
# WHITENOISE_SKIP_WHITENOISE = False ensures middleware processes static files
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_GZIP = not DEBUG
WHITENOISE_SKIP_WHITENOISE = False
# Disable overly aggressive compression threading to prevent missing file errors
WHITENOISE_COMPRESS = False

# Media files configuration
MEDIA_URL = '/media/'
if not HAS_CLOUDINARY:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    os.makedirs(MEDIA_ROOT, exist_ok=True)

# --- CORS & CSRF (Next.js & Prod Security) ---
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG:
    FRONTEND_URL = os.environ.get('FRONTEND_URL', "https://utamuwetu.vercel.app")
    CORS_ALLOWED_ORIGINS = [FRONTEND_URL]
    CSRF_TRUSTED_ORIGINS = [FRONTEND_URL]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization', 
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# --- GRAPHENE ---
GRAPHENE = {
    'SCHEMA': 'core.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'