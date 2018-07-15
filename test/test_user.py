import test_setup
import unittest

from django.contrib.auth import authenticate, get_user_model, get_user

''' TO-DO: New test cases to add
username field: 
Case #1a - Input e-mail that already exists as username (FAIL)
Case #1b - Input e-mail that already exists as e-mail (FAIL)
Case #2 - Input e-mail, leave emailaddress field blank --> emailaddress field should populate
Case #3 - Input non-email that already exists as username (FAIL)

emailaddress field:
Case #1 - Input email that already exists as username (FAIL)
Case #2 - Input email that already exist as email (FAIL)
'''

class testUser(unittest.TestCase):
    def testUser(self):
        
        USERNAME = 'oroku'
        EMAILADDRESS = 'hamato@yoshi.com'
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
        self.assertTrue(allusers)
 
        # Authentication user lookup
        self.assertTrue(get_user_model().objects.get_user_auth(None, EMAILADDRESS)) # positive
        self.assertTrue(get_user_model().objects.get_user_auth(USERNAME, None)) # positive
        self.assertFalse(get_user_model().objects.get_user_auth(None, 'wrongemail')) # negative
        self.assertFalse(get_user_model().objects.get_user_auth('elsha', None)) # negative

        # Save to DB
        newuserget.firstname = 'New first name'
        newuserget.save()
        newuser1 = get_user_model().objects.get_user(newuserget.userid)
        
        self.assertEqual(newuser1.firstname, 'New first name')

        # Check user roles - regular user
        self.assertEqual(newuser1.userrole,"U")
        self.assertFalse(newuser1.is_admin())
        self.assertFalse(newuser1.is_superuser())

        # Check user roles - admin
        newuser1.userrole = 'A'
        newuser1.save()
        newuser2 = get_user_model().objects.get_user(newuser1.userid)
        self.assertTrue(newuser2.is_admin())
        self.assertFalse(newuser2.is_superuser())

        # Check user roles - super user
        newuser2.userrole = 'S'
        newuser2.save()
        newuser3 = get_user_model().objects.get_user(newuser2.userid)
        self.assertTrue(newuser3.is_admin())
        self.assertTrue(newuser3.is_superuser())

        # Delete user
        newuser1.delete()
        
        self.assertIsNone(get_user_model().objects.get_user(newuser1.userid))

if __name__ == '__main__':
    unittest.main() # Run all tests