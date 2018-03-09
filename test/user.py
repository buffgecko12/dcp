import test_setup

from django.contrib.auth import authenticate, get_user_model

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
