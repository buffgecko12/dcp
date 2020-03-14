from .base import *

DEBUG = True
ALLOWED_HOSTS += [
    'localhost','127.0.0.1','10.0.0.1', # development
    'dcp2-tst.herokuapp.com','tst.duitamacolegioproject.org', # test
    ]