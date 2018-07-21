from .base import *
DEBUG = False

ALLOWED_HOSTS += ['thawing-spire-81058.herokuapp.com',]

# Configure Django App for Heroku.
django_heroku.settings(locals())
