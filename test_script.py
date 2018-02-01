import django
import os
import sys
from django.contrib.auth import authenticate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'dcp.settings.dev'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings.dev")

django.setup()

from django.contrib.auth import get_user_model

# Create new user
newuser = get_user_model().objects.create_user(
    password = 'adminadmin', 
    usertype = 'ST', 
    firstname = 'Test', 
    lastname = 'Orama'
)

# Get an existing user
newuser2 = get_user_model().objects.get_user(newuser.userid)
print ("New user: ", str(newuser.userid), newuser.get_email_field_name())

print(newuser2.password)
newuser2.set_password('fart')
newuser2.save()
print(newuser2.password)

fart = authenticate(username=newuser2.userid,password='fart')
print (fart.is_authenticated)
