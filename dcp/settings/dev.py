from .base import *

DEBUG = True
ALLOWED_HOSTS += [
    'localhost','127.0.0.1','192.168.0.2','192.168.0.3', # development
    'dcp2-tst.herokuapp.com','tst.duitamacolegioproject.org', # test
    ]