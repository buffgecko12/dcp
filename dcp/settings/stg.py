from .base import *

DEBUG = False
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS += [
    'dcp2-stg.herokuapp.com','stg.duitamacolegioproject.org' # staging
    ]