import django
import os
import sys
from django.contrib.auth import authenticate, get_user_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'dcp.settings.dev'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dcp.settings.dev")

django.setup()

# Create new user
newuser = get_user_model().objects.create_user(
    password = 'adminadmin', 
    usertype = 'ST', 
    firstname = 'Test', 
    lastname = 'Orama',
    username = 'buffgecko',
    emailaddress = 'fart@poop.com'
)

# Get an existing user
try:
    newuser2 = get_user_model().objects.get(newuser.userid)
    print(newuser2)
except get_user_model().DoesNotExist:
    print("No user found")

fart = authenticate(username='fart@poop.com',password='adminadmin')
print("Authenticating...", end="")
if(fart):
    print (fart.is_authenticated)
else:
    print(False)
