import django
import os
import sys
from psycopg2 import Binary

def get_basedir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_abs_path(file_path):
    return os.path.join(get_basedir(), file_path)

def readfile(file_path):
    
    itemfile = open(get_abs_path(file_path),'rb')
    mydatafile = itemfile.read()
    myfile = Binary(mydatafile)
    itemfile.close()
    
    return myfile

BASE_DIR = get_basedir()
sys.path.append(BASE_DIR)

# TO-DO: May need to add check here to determine which module to use
os.environ['DJANGO_SETTINGS_MODULE'] = 'dcp.settings.dev'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings.dev")

django.setup()
