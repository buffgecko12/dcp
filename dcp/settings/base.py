''' 
Django version: 2.0.1
Settings: https://docs.djangoproject.com/en/2.0/topics/settings/
Quick-start: https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
Internationalization: https://docs.djangoproject.com/en/2.0/topics/i18n/
'''

import os
from decouple import config

import django_heroku
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    'users.apps.UsersConfig',
    'wakemeup.apps.WakemeupConfig',
    'crispy_forms',
    'django_tables2',
    'django.contrib.humanize',
    'widget_tweaks',    
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
#                 'dcp.contextprocessor.userinfo'
            ],
        },
    },
]

WSGI_APPLICATION = 'dcp.wsgi.application'

DATABASES = {}
DATABASE_URL = 'postgres://' + \
                config('DB_USER') + ':' + \
                config('DB_PASSWORD') + '@' + \
                config('DB_HOST') + ':' + \
                config('DB_PORT') + '/' + \
                config('DB_NAME') + \
                '?currentSchema=' + config('DB_SCHEMA_NAME')
# DATABASES['default'] = dj_database_url.config(default=DATABASE_URL,conn_max_age=600, ssl_require=True)

# # Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': config('DB_NAME'), # DatabaseName
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'OPTIONS': {
#             'options': '-c search_path=' + config('DB_SCHEMA_NAME') # default schema name
#         },
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'es-CO'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/' # Url for static file serving
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),] # Search directories for static files (otherwise, engine only searches within app directories

# Other settings
LOGIN_REDIRECT_URL = '/' # Where to redirect login requests if "next" is not specified
LOGOUT_REDIRECT_URL = 'wakemeup:index' # Where to redirect login requests if "next" is not specified
AUTH_USER_MODEL = 'users.MyUser' # Custom user model
AUTHENTICATION_BACKENDS=['users.backends.MyBackend']
# MAX_UPLOAD_SIZE = 5242880 # Limit max file upload size for RestrictedFileField class
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # Kill session on browser close

CRISPY_TEMPLATE_PACK = 'bootstrap4' # Set default template for forms
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap-responsive.html' # Set default template for tables