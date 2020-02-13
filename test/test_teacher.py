import unittest
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
        cls.myteacher1 = create_user(usertype='TR')
        cls.myteacher2 = create_user(usertype='TR')
    
    def setUp(self):
        self.myteacherclass1 = create_teacher_class(self.myteacher1.userid, self.myclass1.classid)
        self.myteacherclass2 = create_teacher_class(self.myteacher1.userid, self.myclass2.classid)
        
        TeacherClass(teacheruserid=self.myteacher2.userid,classid=None).save(classidlist=[self.myclass1.classid, self.myclass2.classid])
        
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
        self.myteacherclass1.delete()
        self.assertFalse(refresh(self.myteacherclass1))

    def tearDown(self):        
        self.myteacherclass1.delete()
        self.myteacherclass2.delete()
        
    @classmethod
    def tearDownClass(cls):
        cls.myteacher1.delete()
        cls.myteacher2.delete()
        cls.myschool.delete()
        
if __name__ == '__main__':
    unittest.main() # Run all tests