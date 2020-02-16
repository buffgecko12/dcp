import unittest
from test_setup import *
from user.models.authorization import *

class testAuthorization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.myteacher1 = create_user(usertype='TR')
        cls.myteacher2 = create_user(usertype='TR')
        cls.mystudent = create_user(usertype='ST')
        cls.myadmin = create_user(usertype='AD')
        cls.mysuperuser = create_user(usertype='SU')
        
        cls.myfile1 = create_file(filename='Some document')
        cls.myfile2 = create_file(filename='Contract form')
        
    def setUp(self):
        
        # Roles
        self.myrole_all = create_role(name="All",userlist=[self.myteacher1.userid,self.myteacher2.userid,self.mystudent.userid],usertypelist=['TR','ST','AD','SF'],publicflag=True)
        self.myrole_twousers = create_role(name="User 1 and User 2",userlist=[self.myteacher1.userid,self.myteacher2.userid])
        self.myrole_oneuser = create_role(name="User 3",userlist=[self.mystudent.userid])
        self.myrole_teachers = create_role(name="Teachers",usertypelist=['TR'])
        self.myrole_admin = create_role(name="Administration",usertypelist=['AD'])
        self.myrole_public = create_role(name="Public",publicflag=True)
        
        # Objects
        self.myobject1 = create_object(objectclass='BO', objectname='contract') # teachers / site admin / super user
        self.myobject2 = create_object(objectclass='BO', objectname='class') # site admin / super user
        self.myobject3 = create_object(objectclass='VW', objectname='some_view')
        
        # ACLs
        self.myroleacl1 = create_role_ACL(self.myrole_public.roleid,self.myfile2.fileid,'FL',4) # Read access to "Public"
        self.myroleacl2 = create_role_ACL(self.myrole_teachers.roleid,self.myfile2.fileid,'FL',8) # Edit access to "Teachers"
        self.myroleacl3 = create_role_ACL(self.myrole_admin.roleid,self.myfile2.fileid,'FL',12) # Delete access to file
        self.myroleacl4 = create_role_ACL(self.myrole_teachers.roleid,self.myobject1.objectid,self.myobject1.objectclass,4) # Read access to "Teachers"

    def testCheckAuthorization(self):
        self.assertTrue(self.myteacher1.check_access(self.myfile2.fileid,'FL',1)) # Browse
        self.assertTrue(self.myteacher1.check_access(self.myfile2.fileid,'FL')) # Default read
        self.assertFalse(self.myteacher1.check_access(self.myfile2.fileid,'FL',12)) # Edit
    
    def testcreateRoleACL(self):
        pass
    
    def testGetRoleACL(self):
        self.assertIsNotNone(refresh(self.myroleacl1))
        self.assertFalse(RoleACL.objects.get_role_acls(objectid=self.myfile1.fileid))
        self.assertTrue(RoleACL.objects.get_role_acls(objectid=self.myfile2.fileid,objectclass='FL',accesslevel=8))
        self.assertTrue(RoleACL.objects.all())
        
    def testUpdateRoleACL(self):
        self.assertTrue(self.myroleacl1.accesslevel,4)
        self.myroleacl1.accesslevel=8
        self.myroleacl1.save()
        self.myroleacl1 = refresh(self.myroleacl1)
        self.assertTrue(self.myroleacl1.accesslevel,8)
        
    def testDeleteRoleACL(self):
        self.assertTrue(refresh(self.myroleacl1))
        self.myroleacl1.delete()
        self.assertFalse(refresh(self.myroleacl1))

    def testCreateObject(self):
        pass
    
    def testGetObject(self):
        self.assertIsNotNone(refresh(self.myobject1))
        self.assertTrue(Object.objects.get_objects(objectclass='BO')) # Files
        self.assertTrue(Object.objects.all()) # All
        
    def testUpdateObject(self):
        self.assertTrue(self.myobject1.objectname,'contract')
        self.myobject1.objectname='contracts'
        self.myobject1.save()
        self.myobject1 = refresh(self.myobject1)
        self.assertTrue(self.myobject1.objectname,'contracts') 
        
    def testDeleteObject(self):
        
        self.assertTrue(refresh(self.myobject1))
        self.myobject1.delete()
        self.assertIsNone(refresh(self.myobject1))
        
    def testCreateRole(self):
        pass

    def testModifyRoleItem(self):
        
        # Add specific student to Teachers role
        self.myrole_teachers.modify_role_item(userid=self.mystudent.userid)
        self.myrole_teachers.modify_role_item(userid=self.mystudent.userid,changetype='D') # Delete
        
        # Addd usertype to specific role
        self.myrole_teachers.modify_role_item(usertype='AD')
        self.myrole_teachers.modify_role_item(usertype='AD',changetype='D') # Delete
        
    def testGetRole(self):
        self.assertIsNotNone(refresh(self.myrole_twousers)) # single role
        self.assertTrue(Role.objects.get_roles(rolename='Teachers'))
        self.assertTrue(Role.objects.all()) # all roles

    def testUpdateRole(self):

        # Check before updates
        self.assertTrue(self.myrole_all.publicflag)
        self.assertTrue(('SF' in (self.myrole_all.usertypelist)))
        self.assertTrue((self.myteacher1.userid in (self.myrole_all.userlist)))
        
        # Make updates
        self.myrole_all.publicflag = False
        self.myrole_all.usertypelist = ['AD','TR']
        self.myrole_all.userlist = [self.myteacher2.userid,self.mystudent.userid]

        # Save and refresh
        self.myrole_all.save()
        self.myrole_all = refresh(self.myrole_all)

        # Verify changes
        self.assertFalse(self.myrole_all.publicflag)
        self.assertFalse(('SF' in (self.myrole_all.usertypelist)))
        self.assertFalse((self.myteacher1.userid in (self.myrole_all.userlist)))

    def testDeleteRole(self):
        
        # Check user exists
        self.assertTrue(refresh(self.myrole_oneuser))
        
        # Verify delete
        self.myrole_oneuser.delete()
        self.assertIsNone(refresh(self.myrole_oneuser))

    def tearDown(self):
        self.myrole_all.delete()
        self.myrole_twousers.delete()
        self.myrole_oneuser.delete()
        self.myrole_teachers.delete()
        self.myrole_admin.delete()
        self.myrole_public.delete()
        
        self.myroleacl1.delete()
        self.myroleacl2.delete()
        self.myroleacl3.delete()
        self.myroleacl4.delete()

    @classmethod
    def tearDownClass(cls):
        cls.myteacher1.delete()
        cls.myteacher2.delete()
        cls.mystudent.delete()
        
        cls.myfile1.delete()
        cls.myfile2.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests