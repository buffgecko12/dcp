import django
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'dcp.settings.dev'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings.dev")

django.setup()

from wakemeup.models import School

if __name__ == '__main__':
    

#     newschool = School(None, 'School name', 'My address','San Diego','CA')    
#     newschoolid = newschool.save()    
#     newschool2 = School.objects.get(newschoolid)


    School.objects.delete(1)

    try:
        fart = School.objects.get(2)

    except School.DoesNotExist:
        print("FART!")
        
