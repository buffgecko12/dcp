from .base import *
DEBUG = False

ALLOWED_HOSTS += ['0.0.0.0', 'localhost', 'thawing-spire-81058.herokuapp.com']

print("BEFORE",ALLOWED_HOSTS)

# Configure Django App for Heroku.
django_heroku.settings(locals())

print("AFTER",ALLOWED_HOSTS)

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