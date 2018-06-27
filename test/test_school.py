import test_setup
import unittest

from wakemeup.models.environment import School

class testSchool(unittest.TestCase):
    
    # Create new school
    def testCreateNewSchool(self):
        newschool = School(None, 'MySchool', 'MyAbbreviation', '123 Fake Ln', 'San Diego', 'CA')
        self.assertEqual(newschool.schooldisplayname, 'MySchool')
        self.assertFalse(newschool.schoolid)
    
        # Save school
        newschoolid = newschool.save()
    
        # Get school
        newschool_get = School.objects.get(newschoolid)

        self.assertEqual(newschool.schooldisplayname, newschool_get.schooldisplayname)
        self.assertTrue(newschool_get.schoolid)
    
        # Get all schools
        allschools = School.objects.all()
        self.assertTrue(allschools)

        # Update school
        newschool_get.address = '123 New address'
        newschool_get.save()

        # Delete school
        newschool_get.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests