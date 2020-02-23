from django.conf import settings

# Get settings file key value
def get_setting(setting):
    return settings.get(setting)

def get_school_year():
    return settings.DEFAULT_SCHOOL_YEAR

def get_objectname(myobject):
    return myobject.__class__.__name__.lower()