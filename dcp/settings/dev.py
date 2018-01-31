from .base import *

DEBUG = True
ALLOWED_HOSTS += ['localhost','127.0.0.1','ravioli.dynu.net','ravioli.freeddns.org']

INSTALLED_APPS += []
MIDDLEWARE += []
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

