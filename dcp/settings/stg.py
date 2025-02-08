from .base import *
import django_on_heroku

DEBUG = False
ALLOWED_HOSTS += [
    'dcp2-stg.herokuapp.com','stg.duitamacolegioproject.org' # staging
    ]

# https://help.heroku.com/J2R1S4T8/can-heroku-force-an-application-to-use-ssl-tls
SECURE_SSL_REDIRECT = True

# Configure app for Heroku: DATABASE_URL, ALLOWED_HOSTS, WhiteNoise (static assets), Logging, Heroku CI
django_on_heroku.settings(locals())

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
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}