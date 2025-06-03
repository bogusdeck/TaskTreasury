"""
Simplified settings for Vercel deployment.
This file imports from the main settings and overrides problematic settings.
"""
import os
import sys
from pathlib import Path

# Import all settings from the main settings file
from main.settings import *

# Simplify logging configuration to avoid formatter issues
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Ensure DEBUG is False in production
DEBUG = False

# Make sure ALLOWED_HOSTS includes Vercel domains
ALLOWED_HOSTS = ['*', '.vercel.app', '.now.sh']

# Configure database - use SQLite for simplicity if DATABASE_URL is not set
import dj_database_url

# Default to SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# If DATABASE_URL is set, use that
database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES['default'] = dj_database_url.parse(database_url)
else:
    # Otherwise, try to use individual database settings
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    
    if db_name and db_user and db_password and db_host:
        # Use PostgreSQL with individual credentials
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': db_name,
                'USER': db_user,
                'PASSWORD': db_password,
                'HOST': db_host,
                'PORT': db_port or '5432',
                'OPTIONS': {
                    'sslmode': os.environ.get('DB_SSLMODE', 'require'),
                },
            },
        }

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
