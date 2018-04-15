import test_setup
import unittest

from django.contrib.auth import authenticate, get_user_model, get_user

class testUser(unittest.TestCase):
    def testUser(self):
        
        USERNAME = 'oroku'
        EMAILADDRESS = 'oroku@saki.com'
        PASSWORD = 'wowzers'
        
        # Create new user
        newuser = get_user_model().objects.create_user(
            password = PASSWORD, 
            usertype = 'ST', 
            firstname = 'Test', 
            lastname = 'Orama',
            username = USERNAME,
            emailaddress = EMAILADDRESS,
            userrole = 'U'
        )
        
        self.assertEqual(newuser.firstname,'Test')
        
        # Get an existing user
        newuserget = get_user_model().objects.get_user(newuser.userid)
        self.assertIsNotNone(newuserget) # positive
        self.assertIsNone(get_user_model().objects.get_user(10000)) # negative

        # Authenticate
        self.assertTrue(authenticate(username=USERNAME,password=PASSWORD)) # positive
        self.assertFalse(authenticate(username=USERNAME,password='wrongpass')) # negative
        self.assertFalse(authenticate(username='wronguser',password=USERNAME)) # negative

        # Get all users
        allusers = get_user_model().objects.all()
         
        for myuser in allusers:
            print (myuser.username)
 
        # Authentication user lookup
        self.assertTrue(get_user_model().objects.get_user_auth(None, EMAILADDRESS)) # positive
        self.assertTrue(get_user_model().objects.get_user_auth(USERNAME, None)) # positive
        self.assertFalse(get_user_model().objects.get_user_auth(None, 'wrongemail')) # negative
        self.assertFalse(get_user_model().objects.get_user_auth('elsha', None)) # negative

        # Save to DB
        newuserget.firstname = 'New first name'
        newuserget.save()
        newusergetget = get_user_model().objects.get_user(newuserget.userid)
        
        self.assertEqual(newusergetget.firstname, 'New first name')

        # Admin checks
        self.assertIsNotNone(newusergetget.is_admin())
        self.assertIsNotNone(newusergetget.is_superuser())

        # Delete user
        newusergetget.delete()
        
        self.assertIsNone(get_user_model().objects.get_user(newusergetget.userid))

if __name__ == '__main__':
    unittest.main() # Run all tests