import unittest
from test_setup import *
from user.models.authorization import *

class testAuthorization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.myuser1 = create_user()
        cls.myuser2 = create_user()
        cls.myuser3 = create_user()
        
    def setUp(self):
        self.myrole_all = create_role(name="All",userlist=[self.myuser1.userid,self.myuser2.userid,self.myuser3.userid],usertypelist=['TR','ST','AD','SF'],publicflag=True)
        self.myrole_userid_m = create_role(name="User 1 and User 2",userlist=[self.myuser1.userid,self.myuser2.userid])
        self.myrole_userid_s = create_role(name="User 3",userlist=[self.myuser3.userid])
        self.myrole_usertype_m = create_role(name="Teachers and students",usertypelist=['TR','ST'])
        self.myrole_usertype_s = create_role(name="Administration",usertypelist=['AD'])
        self.myrole_public = create_role(name="Public",publicflag=True)
    
    def testCreateRole(self):
        pass

    # TODO
    def testCheckAuthorization(self):
        pass

    def testGetRole(self):
        self.assertIsNotNone(refresh(self.myrole_userid_m)) # single role
        self.assertTrue(Role.objects.all()) # all roles

    def testUpdateRole(self):

        # Check before updates
        self.assertTrue(self.myrole_all.publicflag)
        self.assertTrue(('SF' in (self.myrole_all.usertypelist)))
        self.assertTrue((self.myuser1.userid in (self.myrole_all.userlist)))
        
        # Make updates
        self.myrole_all.publicflag = False
        self.myrole_all.usertypelist = ['AD','TR']
        self.myrole_all.userlist = [self.myuser2.userid,self.myuser3.userid]

        # Save and refresh
        self.myrole_all.save()
        self.myrole_all = refresh(self.myrole_all)

        # Verify changes
        self.assertFalse(self.myrole_all.publicflag)
        self.assertFalse(('SF' in (self.myrole_all.usertypelist)))
        self.assertFalse((self.myuser1.userid in (self.myrole_all.userlist)))

    def testDeleteRole(self):
        
        # Check user exists
        self.assertTrue(refresh(self.myrole_userid_s))
        
        # Verify delete
        self.myrole_userid_s.delete()
        self.assertIsNone(refresh(self.myrole_userid_s))
    
    def cleanUp(self):
        self.myrole_userid_m.delete()
        self.myrole_userid_s.delete()
        self.myrole_usertype_m.delete()
        self.myrole_usertype_s.delete()
        self.myrole_public.delete()

    @classmethod
    def cleanUpClass(cls):
        self.myuser1.delete()
        self.myuser2.delete()
        self.myuser3.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests