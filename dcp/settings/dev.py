from .base import *

DEBUG = True
ALLOWED_HOSTS += ['localhost','127.0.0.1','ravioli.dynu.net','ravioli.freeddns.org','192.168.50.41']

INSTALLED_APPS += []
MIDDLEWARE += []
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configure Django App for Heroku.
import django_heroku
django_heroku.settings(locals())