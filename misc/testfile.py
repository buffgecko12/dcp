import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcp.settings.dev')
django.setup()

from lib.UsefulFunctions.googleUtils import GoogleDrive
from wakemeup.models.environment import File

if __name__ == "__main__":

    gd = GoogleDrive()
    result = gd.sync(fileid='1kiU01bASsOfcJkLJxT06lIExVurTr8hr')
    print(result)