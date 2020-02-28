from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS += ['localhost','127.0.0.1','192.168.0.2','192.168.0.3','dcp2-tst.herokuapp.com']