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
    global clean_user
    global create_user

    global USERNAME
    global EMAILADDRESS
    global PASSWORD

    USERNAME = 'oroku'
    EMAILADDRESS = 'hamato@yoshi.com'
    PASSWORD = 'wowzers'
    
    def clean_user(username):
        # Delete user if exists
        try:
            checkuser = get_user_model().objects.get(username = USERNAME)
            checkuser.delete()
        except:
            pass

    def create_user(password, username, usertype, firstname, lastname, emailaddress, userrole):
        
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

        return newuser

    def testUser(self):

        clean_user(USERNAME)
        newuser = create_user(password=PASSWORD,usertype='ST',firstname='Test',lastname='Orama',username=USERNAME,emailaddress=EMAILADDRESS,userrole='U')
        
        self.assertEqual(newuser.firstname,'Test')
        
        # Get an existing user
        nenwuser = get_user_model().objects.get_user(newuser.userid)
        self.assertIsNotNone(nenwuser) # positive
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
        nenwuser.firstname = 'New first name'
        nenwuser.save_user()
        newuser = get_user_model().objects.get_user(nenwuser.userid)
        
        self.assertEqual(newuser.firstname, 'New first name')

        # Check user roles - regular user
        self.assertEqual(newuser.userrole,"U")
        self.assertFalse(newuser.is_admin())
        self.assertFalse(newuser.is_superuser())

        # Check user roles - admin
        newuser.userrole = 'A'
        newuser.save_user()
        newuser = get_user_model().objects.get_user(newuser.userid)
        self.assertTrue(newuser.is_admin())
        self.assertFalse(newuser.is_superuser())

        # Check user roles - super user
        newuser.userrole = 'S'
        newuser.save_user()
        newuser = get_user_model().objects.get_user(newuser.userid)
        self.assertTrue(newuser.is_admin())
        self.assertTrue(newuser.is_superuser())

        # Delete user
        newuser.delete()

        self.assertIsNone(get_user_model().objects.get_user(newuser.userid))


if __name__ == '__main__':
    unittest.main() # Run all tests