from .base import *
DEBUG = False

ALLOWED_HOSTS += ['.herokuapp.com',]

# Configure Django App for Heroku.
django_heroku.settings(locals())
