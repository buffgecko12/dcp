import unittest
from test_setup import *

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

    @classmethod
    def setUpClass(cls):
        
        cls.USERNAME = 'oroku'
        cls.EMAILADDRESS = 'hamato@yoshi.com'
        cls.PASSWORD = 'wowzers'
    
    def setUp(self):
        self.myuser = create_user(password=self.PASSWORD,username=self.USERNAME,emailaddress=self.EMAILADDRESS)
    
    def testCreateUser(self):
        pass
    
    def testGetUser(self):
        
        self.assertEqual(self.myuser.username,self.USERNAME)
        
        # Get an existing user
        self.myuser = refresh(self.myuser)
        self.assertIsNotNone(self.myuser) # positive
        self.assertIsNone(get_user_model().objects.get_user(10000)) # negative

        # Get all users
        self.assertTrue(get_user_model().objects.all())

    def testUpdateUser(self):

        newname = 'New first name'
        
        self.myuser.firstname = newname
        self.myuser.save_user()
        self.myuser = refresh(self.myuser)
        
        self.assertEqual(self.myuser.firstname, newname)

    def testDeleteUser(self):
        
        # Check user exists
        self.assertTrue(refresh(self.myuser))
        
        # Verify delete
        self.myuser.delete()
        self.assertIsNone(get_user_model().objects.get_user(self.myuser.userid))
        self.assertIsNotNone(get_user_model().objects.get_user(self.myuser.userid,activeflag=False))
    
    def testAuthenticateUser(self):

        # Authenticate
        self.assertTrue(authenticate(username=self.USERNAME,password=self.PASSWORD)) # positive
        self.assertFalse(authenticate(username=self.USERNAME,password='wrongpass')) # negative
        self.assertFalse(authenticate(username='wronguser',password=self.USERNAME)) # negative

 
        # Authentication user lookup
        self.assertTrue(get_user_model().objects.get_user_auth(None, self.EMAILADDRESS)) # positive
        self.assertTrue(get_user_model().objects.get_user_auth(self.USERNAME, None)) # positive
        self.assertFalse(get_user_model().objects.get_user_auth(None, 'wrongemail')) # negative
        self.assertFalse(get_user_model().objects.get_user_auth('elsha', None)) # negative

    def testCheckUserType(self):

        # Check user roles - regular user
        self.assertFalse(self.myuser.is_admin())
        self.assertFalse(self.myuser.is_superuser())

        # Check user roles - admin
        self.myuser.usertype = 'AD'
        self.myuser.save_user()
        self.myuser = refresh(self.myuser)
        self.assertTrue(self.myuser.is_admin())
        self.assertFalse(self.myuser.is_superuser())

        # Check user roles - super user
        self.myuser.usertype = 'SU'
        self.myuser.save_user()
        self.myuser = refresh(self.myuser)
        self.assertTrue(self.myuser.is_admin())
        self.assertTrue(self.myuser.is_superuser())

    def testUserMisc(self):
        
        # Test default profile picture inserts
        self.assertIsNotNone(get_user_model().objects.get_profile_picture_options(self.myuser.userid))

        # Test e-mail
        self.myuser.send_email(email_subject='test',email_body='test body')

    def testMakeRandomPassword(self):

        mypass = get_user_model().objects.make_random_password(length=15)
        self.assertEqual(len(mypass), 15)

    def cleanUp(self):

        # Delete user
        self.myuser.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests