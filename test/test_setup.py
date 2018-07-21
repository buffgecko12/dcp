import django
import os
import sys
from psycopg2 import Binary

def get_basedir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def readfile(myfilepath):
    # Read in "signature" file
    BASE_DIR = get_basedir()
    
    filepath = os.path.join(BASE_DIR,myfilepath)

    itemfile = open(filepath,'rb')
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
