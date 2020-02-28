from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS += [
    'localhost','127.0.0.1','192.168.0.2','192.168.0.3', # development
    'dcp2-tst.herokuapp.com','dev.duitamacolegioproject.org', # test
    'dcp2-stg.herokuapp.com','stg.duitamacolegioproject.org' # staging
    ]