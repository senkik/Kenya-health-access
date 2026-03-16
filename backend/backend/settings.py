
import os
from pathlib import Path
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

# GeoDjango / GDAL Setup
if os.name == 'nt':  # Windows
    OSGEO4W_ROOT = os.environ.get('OSGEO4W_ROOT', r"C:\OSGeo4W")
    if os.path.isdir(OSGEO4W_ROOT):
        os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + os.pathsep + os.environ['PATH']
        # Try to find the dlls
        for ver in ['309', '308', '307', '306', '305', '']:
            gdal_path = os.path.join(OSGEO4W_ROOT, 'bin', f'gdal{ver}.dll')
            if os.path.isfile(gdal_path):
                GDAL_LIBRARY_PATH = gdal_path
                break
        GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'geos_c.dll')
else:  # Linux (Render)
    GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
    GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')

NGROK_URL = os.getenv('NGROK_URL', 'sphygmographic-unrising-farah.ngrok-free.dev')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')

ALLOWED_HOSTS = [
    'localhost',
    'kenya-health-api.onrender.com',
    '.onrender.com',
    '127.0.0.1',
    'sphygmographic-unrising-farah.ngrok-free.dev',  # Add this
    '.ngrok-free.dev',  # Allow all ngrok domains
    '.ngrok.io',        # For other ngrok URLs
]


# Application
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    'django.contrib.gis',
    # Local apps
    'facilities',
    'locations',
    'ussd',
    'api',
    'content',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be FIRST
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
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# Use PostgreSQL if configured, otherwise fall back to SQLite
if os.getenv('USE_POSTGRES') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'kenya_health_access'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'IamHim@123'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Africa's Talking Configuration
AT_USERNAME = os.getenv('AT_USERNAME', 'sandbox')
AT_API_KEY = os.getenv('AT_API_KEY', 'atsk_b8d731cae5157044bda8513bc68c4d304a9c5a131c7974a8c38696a55662561c35c624a2')

# Redis Cache Configuration
if os.getenv('USE_REDIS') == 'True':
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'kenya_health',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }
    # Use Redis for sessions
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes



# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# API Documentation (drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Kenya Health Access API',
    'DESCRIPTION': 'API for accessing healthcare facility information across Kenya',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CSRF_TRUSTED_ORIGINS = [
    'https://sphygmographic-unrising-farah.ngrok-free.dev',
    'https://*.ngrok-free.dev',
    'https://kenya-health-access.vercel.app',
    'https://kenya-health-api.onrender.com',
]

# Security settings for ngrok
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True


# Allow your Vercel frontend
CORS_ALLOWED_ORIGINS = [
    "https://kenya-health-access.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

# Allow credentials
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings
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

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CSRF_TRUSTED_ORIGINS = [
    "https://kenya-health-access.vercel.app",
    "https://kenya-health-api.onrender.com",
    'https://sphygmographic-unrising-farah.ngrok-free.dev',
]

ALLOWED_HOSTS = [
    'kenya-health-api.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

SESSION_COOKIE_SAMESITE = 'None'  # Only if using cross-site cookies
SESSION_COOKIE_SECURE = True      # Required for SameSite=None
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# Operator API Keys (add to .env)
SAFARICOM_API_KEY = os.getenv('SAFARICOM_API_KEY')
SAFARICOM_API_SECRET = os.getenv('SAFARICOM_API_SECRET')
AIRTEL_API_KEY = os.getenv('AIRTEL_API_KEY')
TELKOM_API_KEY = os.getenv('TELKOM_API_KEY')
OPERATOR_SECRETS = {
    'safaricom': SAFARICOM_API_SECRET,
    'telkom': os.getenv('TELKOM_API_SECRET'),
}

# Africa's Talking for SMS
AT_USERNAME = os.getenv('AT_USERNAME', 'sandbox')
AT_API_KEY = os.getenv('AT_API_KEY')
AFRICASTALKING_USERNAME = AT_USERNAME
AFRICASTALKING_API_KEY = AT_API_KEY
SMS_SENDER_ID = os.getenv('SMS_SENDER_ID', 'HUDUMA')

# Celery for async tasks
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'
USE_DEMO_LOCATION = os.getenv('USE_DEMO_LOCATION', 'False') == 'True'