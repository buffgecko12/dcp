import unittest
from test_setup import *
from user.models.authorization import *
from lib.UsefulFunctions.dataUtils import * 

class testAuthorization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        # School
        cls.myschool1 = create_school(schoolabbreviation='School1')
        cls.myschool2 = create_school(schoolabbreviation='School2')
        cls.myclass1 = create_class(schoolid=cls.myschool1.schoolid)
        
        # Users
        cls.myteacher1 = create_user(usertype='TR', schoolid=cls.myschool1.schoolid)
        cls.myteacher2 = create_user(usertype='TR', schoolid=cls.myschool2.schoolid)
        cls.myteacherclass1 = create_teacher_class(cls.myteacher1.userid,cls.myclass1.classid)
        cls.mystudent = create_user(usertype='ST', schoolid=cls.myschool1.schoolid)
        cls.myadmin = create_user(usertype='AD')
        cls.mysuperuser = create_user(usertype='SU')

        # Contract
        cls.mycontract = create_contract()
        cls.mycontractparty = create_contract_party(cls.mycontract.contractid,cls.myteacherclass1.teacheruserid,cls.myteacherclass1.classid)
        
        # Files        
        cls.myfile1 = create_file(filename='Some document')
        cls.myfile2 = create_file(filename='Contract form')
        cls.myfile3 = create_file(filename='Public document')
        cls.myfile4 = create_file(filename='Welcome video - School 1')
        cls.myfile5 = create_file(filename='Teachers only file - School 1')
        cls.myfile6 = create_file(filename='Welcome video - School 2')
        cls.myfile7 = create_file(filename='Contract File - Teacher 1',contractid=cls.mycontract.contractid)
        
    def setUp(self):
        
        # Roles
        self.myrole_all = create_role(name="All",userlist=[self.myteacher1.userid,self.myteacher2.userid,self.mystudent.userid],usertypelist=['TR','ST','AD','SF'],publicflag=True)
        self.myrole_twousers = create_role(name="User 1 and User 2",userlist=[self.myteacher1.userid,self.myteacher2.userid])
        self.myrole_oneuser = create_role(name="User 3",userlist=[self.mystudent.userid])
        self.myrole_teachers = create_role(name="Teachers_test",usertypelist=['TR'])
        self.myrole_admin = create_role(name="Administration_test",usertypelist=['AD'])
        self.myrole_public = create_role(name="Public_test",publicflag=True)
        
        # Objects
        self.myobject1 = create_object(objectclass='BO', objectname='contract_test')
        
        # ACLs
        self.myroleacl1 = create_role_ACL(self.myrole_public,self.myfile2,4) # Read access to "Public"
        self.myroleacl2 = create_role_ACL(self.myrole_teachers,self.myfile2,8) # Edit access to "Teachers"
        self.myroleacl3 = create_role_ACL(self.myrole_admin,self.myfile2,12) # Delete access to file
        self.myroleacl4 = create_role_ACL(self.myrole_teachers,self.myobject1,4) # Read access to "Teachers"

        # ACLS - School
        self.myroleacl5 = create_role_ACL(Role(roleid=self.myschool1.defaultroleids['school']),self.myfile4,4) # Read access to school
        self.myroleacl6 = create_role_ACL(Role(roleid=self.myschool1.defaultroleids['teachers']),self.myfile5,8) # Read access to teachers at a school

        # ACLS - Public
        self.myroleacl7 = create_role_ACL(self.myrole_public,self.myfile3,4)

    def testCheckAuthorization(self):
        
        self.assertFalse(self.myteacher1.check_access(-1,'FL',1)) # Invalid file 
        
        # Access levels
        self.assertTrue(self.myteacher1.check_access(self.myfile2.fileid,'FL',1)) # Browse
        self.assertTrue(self.myteacher1.check_access(self.myfile2.fileid,'FL')) # Default read
        self.assertFalse(self.myteacher1.check_access(self.myfile2.fileid,'FL',12)) # Edit
        
        # Public
        self.assertTrue(self.mystudent.check_access(self.myfile3.fileid,'FL',4))
        self.assertFalse(self.mystudent.check_access(self.myfile3.fileid,'FL',8))
    
        # User
        self.myroleacl = create_role_ACL(self.myrole_oneuser,self.myfile3,8) # Edit access to file
        self.assertTrue(self.mystudent.check_access(self.myfile3.fileid,'FL',8))

        # School
        self.assertTrue(self.mystudent.check_access(self.myfile4.fileid,'FL',4))
        self.assertFalse(self.mystudent.check_access(self.myfile4.fileid,'FL',8))
        self.assertFalse(self.myteacher2.check_access(self.myfile4.fileid,'FL',1))

        # Teacher (UserType)
        self.assertTrue(self.myteacher1.check_access(self.myobject1.objectid,self.myobject1.objectclass,4))
        self.assertTrue(self.myteacher2.check_access(self.myobject1.objectid,self.myobject1.objectclass,4))
        self.assertFalse(self.myteacher1.check_access(self.myobject1.objectid,self.myobject1.objectclass,8))
        self.assertFalse(self.mystudent.check_access(self.myobject1.objectid,self.myobject1.objectclass,1))
        
        # Teacher (UserType) at a school
        self.assertTrue(self.myteacher1.check_access(self.myfile5.fileid,'FL',8))
        self.assertFalse(self.myteacher1.check_access(self.myfile4.fileid,'FL',8))
        self.assertFalse(self.myteacher2.check_access(self.myfile4.fileid,'FL',8))

        # Contract-related
        self.assertTrue(self.myteacher1.check_access(self.myfile7.fileid,'FL',4))
        self.assertFalse(self.myteacher1.check_access(self.myfile7.fileid,'FL',8))
        self.assertFalse(self.myteacher2.check_access(self.myfile7.fileid,'FL',1))
        self.assertFalse(self.mystudent.check_access(self.myfile7.fileid,'FL',1))

    def testRevokedAuthorization(self):
        
        # Check before
        self.assertTrue(self.mystudent.check_access(self.myfile3.fileid,'FL',1))

        # Revoke access and check again
        self.myroleacl7.accesslevel = 0
        self.myroleacl7.save()
        self.assertFalse(self.mystudent.check_access(self.myfile3.fileid,'FL',1)) # No access
    
    def testUndefinedAuthorization(self):
        
        # Check before
        self.assertTrue(self.mystudent.check_access(self.myfile3.fileid,'FL',1))
        
        # Delete access and check again
        self.myroleacl7.delete()
        self.assertFalse(self.mystudent.check_access(self.myfile3.fileid,'FL',1))
    
    def testcreateRoleACL(self):
        pass
    
    def testGetRoleACL(self):
        self.assertIsNotNone(refresh(self.myroleacl1))
        self.assertFalse(RoleACL.objects.get_role_acls(objectid=self.myfile1.fileid,objectclass='FL'))
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

    def testCreateRoleACLBatch(self):
        
        self.assertFalse(self.myteacher1.check_access(self.myobject1.objectid,self.myobject1.objectclass,8)) # Teacher - no edit access
        self.assertFalse(self.myadmin.check_access(self.myobject1.objectid,self.myobject1.objectclass,1)) # Admin - no edit access
        
        # Grant ACLs on contracts
        myacllist = to_json([
            # Teachers
            {"roleid":self.myrole_teachers.roleid, "aclinfo":
                [
                    {"objectid":self.myobject1.objectid,"objectclass":self.myobject1.objectclass,"accesslevel":8}, # object1 - edit
                ]
            },
            
            # Admin
            {"roleid":self.myrole_admin.roleid, "aclinfo":
                [
                    {"objectid":self.myobject1.objectid,"objectclass":self.myobject1.objectclass,"accesslevel":12}, # object1 - delete
                ]
            },
        ])

        # Batch save
        create_role_ACL(myrole=None,myobject=None,accesslevel=None,acllist=myacllist) # Read access to "Public"
        
        self.assertTrue(self.myteacher1.check_access(self.myobject1.objectid,self.myobject1.objectclass,8)) # Teacher - no edit access
        self.assertTrue(self.myadmin.check_access(self.myobject1.objectid,self.myobject1.objectclass,12)) # Admin - no edit access
        
        # Delete ACLs
        RoleACL(roleid=None,objectid=self.myobject1.objectid,objectclass=self.myobject1.objectclass).delete()

    def testCreateObject(self):
        pass
    
    def testGetObject(self):
        self.assertIsNotNone(refresh(self.myobject1))
        self.assertTrue(Object.objects.get_objects(objectclass='BO')) # Files
        self.assertTrue(Object.objects.get_object_by_name(objectname='contract_test')) # Files
        self.assertFalse(Object.objects.get_object_by_name(objectname='homero')) # Files
        self.assertTrue(Object.objects.all()) # All
        
    def testUpdateObject(self):
        self.assertTrue(self.myobject1.objectname,'contract_test')
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
        
    def testModifyRoleItemDuplicate(self):
        
        # Check initial access (read, but not edit)
        self.assertTrue(self.mystudent.check_access(objectid=self.myfile2.fileid,objectclass='FL',requestedaccesslevel=4))
        self.assertFalse(self.mystudent.check_access(objectid=self.myfile2.fileid,objectclass='FL',requestedaccesslevel=8))

        # Add student twice to teachers role and verify edit access
        for mycount in [1,2]:
            self.myrole_teachers.modify_role_item(userid=self.mystudent.userid)

        self.assertTrue(self.mystudent.check_access(objectid=self.myfile2.fileid,objectclass='FL',requestedaccesslevel=8))

        # Delete and verify
        self.myrole_teachers.modify_role_item(userid=self.mystudent.userid,changetype='D')
        self.assertTrue(self.mystudent.check_access(objectid=self.myfile2.fileid,objectclass='FL',requestedaccesslevel=4))
        self.assertFalse(self.mystudent.check_access(objectid=self.myfile2.fileid,objectclass='FL',requestedaccesslevel=8))
        
    def testGetRole(self):
        self.assertIsNotNone(refresh(self.myrole_twousers)) # single role
        self.assertTrue(Role.objects.get_roles(name='Teachers_test'))
        self.assertTrue(Role.objects.all()) # all roles
        self.assertTrue(Role.objects.get_role_options()) # drop-down

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
        self.myroleacl5.delete()
        self.myroleacl6.delete()
        self.myroleacl7.delete()

        self.myobject1.delete()

    @classmethod
    def tearDownClass(cls):
        cls.myteacher1.delete()
        cls.myteacher2.delete()
        cls.mystudent.delete()
        cls.myadmin.delete()
        cls.mysuperuser.delete()
        
        cls.myfile1.delete()
        cls.myfile2.delete()
        cls.myfile3.delete()
        cls.myfile4.delete()
        cls.myfile5.delete()
        cls.myfile6.delete()
        cls.myfile7.delete()

        cls.myclass1.delete()
        cls.myteacherclass1.delete()

        cls.mycontract.delete() # deletes associated contract objects (i.e. party)

        delete_school(cls.myschool1)
        delete_school(cls.myschool2)

if __name__ == '__main__':
    unittest.main() # Run all tests