#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # Point to correct settings file (depends on "ENV" variable)
    if(os.environ.get('ENV') != 'development'):
        mymodule = 'dcp.settings.prod'
    else:
        mymodule = 'dcp.settings.dev'
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", mymodule)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
