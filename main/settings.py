import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-5!iwk2zzjsd1#3)c_ea#3b=b9$&ud&dnpgbswjw&6xuly6nky@')

DEBUG = os.environ.get('DEBUG', 'True')

ALLOWED_HOSTS = ['*', '.vercel.app', '.now.sh', 'localhost', '127.0.0.1']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "dynamic_forms",
    'assignment_api',
    'authentication',
    'rest_framework',
    'rest_auth',
    'main',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, "main/templates"],
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

WSGI_APPLICATION = 'main.wsgi.app'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database configuration with support for both individual credentials and DATABASE_URL
import dj_database_url

# First try to use DATABASE_URL if it's set
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Use the DATABASE_URL if provided
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
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
    else:
        # Fallback to SQLite if no database configuration is provided
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'authentication.User'

LANGUAGE_CODE = 'en-us'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "main/static")
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Firebase Storage settings
if not DEBUG or os.environ.get('USE_FIREBASE_STORAGE') == 'True':
    try:
        # Try to import and initialize Firebase
        from main.firebase_firestore_config import initialize_firebase
        firebase_app = initialize_firebase()
        
        if firebase_app:
            # Use Firebase Firestore for media storage
            DEFAULT_FILE_STORAGE = 'main.firebase_firestore_storage.FirebaseFirestoreStorage'
            print("Using Firebase Firestore for media storage")
        else:
            # Fallback to default file storage if Firebase initialization fails
            print("WARNING: Firebase initialization failed, using default file storage")
    except Exception as e:
        print(f"ERROR: Could not initialize Firebase: {str(e)}")
        # Firebase initialization failed, use default storage
        pass

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
