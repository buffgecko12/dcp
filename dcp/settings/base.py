''' 
Django version: 2.0.1
Packages: django, psycopg2, python-decouple, django-debug-toolbar, Pillow

Settings: https://docs.djangoproject.com/en/2.0/topics/settings/
Quick-start: https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
Internationalization: https://docs.djangoproject.com/en/2.0/topics/i18n/
'''

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = []

# Define required apps
PREREQ_APPS = [
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Define project apps
PROJECT_APPS = [
    'users.apps.UsersConfig'
]

# Create INSTALLED_APPS setting
INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dcp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates') # Template search directories
            ],
        'APP_DIRS': True, # Search for templates in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
#                'dcp.contextprocessor.userinfo'
            ],
        },
    },
]

WSGI_APPLICATION = 'dcp.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
    }
}

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
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/' # Url for static file serving
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),] # Search directories for static files (otherwise, engine only searches within app directories
# To-do: move general static files to "dcp" app directory

# Other settings
LOGIN_REDIRECT_URL = '/' # Where to redirect login requests if "next" is not specified
AUTH_USER_MODEL = 'users.MyUser' # Custom user model
AUTHENTICATION_BACKENDS=['users.backends.MyBackend']
# MAX_UPLOAD_SIZE = 5242880 # Limit max file upload size for RestrictedFileField class
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Kill session on browser close