from django.conf import settings

# Get settings file key value
def get_app_setting(setting):
    return getattr(settings,setting,None)

def get_school_year():
    return get_app_setting('DEFAULT_SCHOOL_YEAR')

def get_objectname(myobject):
    return myobject.__class__.__name__.lower()