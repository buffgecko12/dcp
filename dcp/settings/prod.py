from .base import *
import django_heroku

DEBUG = False

# Configure Django App for Heroku (DATABASE_URL, ALLOWED_HOSTS, WhiteNoise Logging, Heroku CI)
django_heroku.settings(locals())

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}