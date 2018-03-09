import test_setup
import unittest

from django.contrib.auth import authenticate, get_user_model

class testUser(unittest.TestCase):
    def testUser(self):
        # Create new user
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', 
            usertype = 'ST', 
            firstname = 'Test', 
            lastname = 'Orama',
            username = 'buffgecko',
            emailaddress = 'joe@smith.com'
        )
        
        self.assertEqual(newuser.firstname,'Test')
        
        # Get an existing user
        try:
            newuser2 = get_user_model().objects.get(newuser.userid)
            print(newuser2)
        except get_user_model().DoesNotExist:
            print("No user found")
        
        auth_check = authenticate(username='joe@smith.com',password='adminadmin')
        print("Authenticating...", end="")
        self.assertTrue(auth_check)

        if(auth_check):
            print (auth_check.is_authenticated)
        else:
            print(False)
