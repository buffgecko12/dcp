import unittest
from test_setup import *

from wakemeup.models.school import School

class testSchool(unittest.TestCase):
    
    def setUp(self):
        self.myschool = create_school(schoolabbreviation = "MCHS", schooldisplayname = 'Mount Carmel High School')
    
    def testCreateSchool(self):
        self.assertTrue(self.myschool.schoolid)
        self.assertEqual(self.myschool.schooldisplayname, 'Mount Carmel High School')

    def testGetSchool(self):
        self.assertTrue(School.objects.get(self.myschool.schoolid))
        self.assertTrue(School.objects.all())
        self.assertTrue(School.objects.school_choices(schoolid = self.myschool.schoolid))
        
    def testUpdateSchool(self):    
        self.myschool.schoolabbreviation = 'CMHS'
        self.myschool.save()
        self.assertEqual(self.myschool.schoolabbreviation,'CMHS')

    def testDeleteSchool(self):
        self.myschool.delete()
        self.assertFalse(refresh(self.myschool))

    def tearDown(self):
        self.myschool.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests