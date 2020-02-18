import unittest
from test_setup import *

from wakemeup.models.school import Class, School
    
class testClass(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.myschool = create_school()
    
    def setUp(self):
        self.myclass1 = create_class(schoolid=self.myschool.schoolid, classdisplayname='New class 1')
        self.myclass2 = create_class(schoolid=self.myschool.schoolid, classdisplayname='New class 2', gradelevel=9, schoolyear=2011)
    
    def testCreateClass(self):
        self.assertTrue(self.myclass1.schoolid)

    def testGetClass(self):
        self.assertTrue(Class.objects.get(self.myclass1.classid)) # one class
        self.assertTrue(Class.objects.all()) # all classes
        self.assertTrue(Class.objects.class_choices()) # class choices

    def testUpdateClass(self):
        self.myclass1.classdisplayname = 'NEW NAME'
        self.myclass1.save()
        self.myclass1 = Class.objects.get(classid=self.myclass1.classid) # Refresh object
        self.assertEqual(self.myclass1.classdisplayname, 'NEW NAME')

    def testDeleteClass(self):
        self.myclass1.delete()
        self.assertFalse(refresh(self.myclass1))

    def tearDown(self):        
        self.myclass1.delete()
        self.myclass2.delete()
        
    @classmethod
    def tearDownClass(cls):
        delete_school(cls.myschool)
    
if __name__ == '__main__':
    unittest.main() # Run all tests