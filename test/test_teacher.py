import unittest
import itertools
from test_setup import *

from django.contrib.auth import get_user_model
from wakemeup.models.school import TeacherClass

class testTeacherProgram(unittest.TestCase):
    pass

class testTeacherClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.myschool = create_school()
        cls.myclass1 = create_class(schoolid=cls.myschool.schoolid)
        cls.myclass2 = create_class(schoolid=cls.myschool.schoolid, schoolyear=2011)
        cls.myteacher1 = create_user(usertype='TR',schoolid=cls.myschool.schoolid)
        cls.myteacher2 = create_user(usertype='TR',schoolid=cls.myschool.schoolid)
        
        cls.programname = 'incentives'
    
    def setUp(self):
        self.myteacherclass1 = create_teacher_class(self.myteacher1.userid, self.myclass1.classid)
        self.myteacherclass2 = create_teacher_class(self.myteacher1.userid, self.myclass2.classid)
        
        TeacherClass(teacheruserid=self.myteacher2.userid,classid=None).save(classidlist=[self.myclass1.classid, self.myclass2.classid])
        
        # Teacher program
        for (myteacher, myschoolyear) in itertools.product([self.myteacher1,self.myteacher2],[2018,2019,DEFAULT_SCHOOL_YEAR]):
            create_user_program(userid=myteacher.userid,schoolyear=myschoolyear,schoolid=myteacher.schoolid,programname=self.programname) # TO-DO: Update for multiple schoolid values
        
    def testCreateTeacherClass(self):
        self.assertTrue(self.myteacherclass1.teacheruserid)

    def testGetTeacherClass(self):
        self.assertTrue(TeacherClass.objects.get(self.myteacher1.userid,self.myclass1.classid))
        self.assertTrue(TeacherClass.objects.all())
        self.assertTrue(TeacherClass.objects.get_teacher_classes(teacheruserid=self.myteacher1.userid))
        self.assertFalse(TeacherClass.objects.get(self.myteacher1.userid,-1))

    def testUpsertTeacherClassBatch(self):
        self.assertTrue(TeacherClass.objects.get(self.myteacher2.userid,self.myclass1.classid))

    def testDeleteTeacherClass(self):
        
        # Check object exists before delete
        self.assertTrue(refresh(self.myteacherclass1))
        
        # Delete and verify
        self.myteacherclass1.delete()
        self.assertFalse(refresh(self.myteacherclass1))

    def testCreateTeacherProgram(self):
        pass

    def testGetTeacherProgram(self): # TO-DO: Move "TeacherProgram" to "User" test and update to handle multiple schoolid values
        self.assertTrue(UserProgram.objects.get(userid=self.myteacher1.userid,schoolid=self.myteacher1.schoolid,schoolyear=DEFAULT_SCHOOL_YEAR,programname=self.programname)) # teacher / year
        self.assertTrue(len(UserProgram.objects.get_user_programs(schoolyear=DEFAULT_SCHOOL_YEAR)),2) # year
        self.assertTrue(len(UserProgram.objects.get_user_programs(userid=self.myteacher1.userid)),3) # teacher
        self.assertEqual(UserProgram.objects.get_programyear_options(schoolyear=DEFAULT_SCHOOL_YEAR)[0][0],DEFAULT_SCHOOL_YEAR) # year
        self.assertEqual(len(UserProgram.objects.get_programyear_options(schoolyear=DEFAULT_SCHOOL_YEAR)),1) # no duplicates

    def testDeleteTeacherProgram(self):
        
        # CHeck object exists before delete
        self.assertTrue(UserProgram.objects.get_user_programs(userid=self.myteacher1.userid))
        
        # Delete and verify
        UserProgram(userid=self.myteacher1.userid,programname=self.programname).delete()
        self.assertFalse(UserProgram.objects.get_user_programs(userid=self.myteacher1.userid))
        self.assertTrue(UserProgram.objects.get_user_programs(userid=self.myteacher2.userid))

    def tearDown(self):        
        self.myteacherclass1.delete()
        self.myteacherclass2.delete()
        UserProgram(userid=self.myteacher1.userid,programname=self.programname).delete()
        UserProgram(userid=self.myteacher2.userid,programname=self.programname).delete()
        
    @classmethod
    def tearDownClass(cls):
        cls.myteacher1.delete()
        cls.myteacher2.delete()
        delete_school(cls.myschool)
        
if __name__ == '__main__':
    unittest.main() # Run all tests