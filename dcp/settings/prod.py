from .base import *
DEBUG = False

# Configure Django App for Heroku.
django_heroku.settings(locals())
