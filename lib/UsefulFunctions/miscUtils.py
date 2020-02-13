from django.conf import settings

# Get settings file key value
def get_setting(setting):
    return settings.get(setting)

def get_school_year():
    return settings.DEFAULT_SCHOOL_YEAR