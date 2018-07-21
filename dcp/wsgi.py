"""
WSGI config for dcp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Point to correct settings file (depends on "ENV" variable)
if(os.environ.get('ENV') != 'development'):
    mymodule = 'dcp.settings.prod'
else:
    mymodule = 'dcp.settings.dev'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", mymodule)

application = get_wsgi_application()
