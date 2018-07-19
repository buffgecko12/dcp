from .base import *
import dj_database_url
DEBUG = False

# Configure Django App for Heroku.
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
django_heroku.settings(locals())

