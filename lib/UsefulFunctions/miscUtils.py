from django.conf import settings
import datetime

# Get settings file key value
def get_app_setting(setting):
    return getattr(settings, setting, None)

def get_school_year():
    try:
        return int(get_app_setting('DEFAULT_SCHOOL_YEAR'))
    except:
        return datetime.datetime.now().year

def get_objectname(myobject):
    return myobject.__class__.__name__.lower()