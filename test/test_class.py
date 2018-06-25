import test_setup
import unittest

from wakemeup.models.environment import Class, School
    
class testClass(unittest.TestCase):
    
    def testClass(self):
        # Create new school
        newschool = School(None, 'New School', 'Address', 'San Diego', 'CA')
        newschoolid = newschool.save()
        
        # Create new class object
        newclass = Class(classid = None, schoolid = newschoolid, classdisplayname = 'New class 1')
        newclass2 = Class(classid = None, schoolid = newschoolid, classdisplayname = 'New class 2')

        self.assertEqual(newclass.classdisplayname, 'New class 1')
    
        # Save class to DB
        newclassid = newclass.save()
        newclassid2 = newclass2.save()
    
        # Retrieve newly saved object
        newclassget = Class.objects.get(newclassid)
        
        self.assertTrue(newclassget.classid)
        
        newclassget.classdisplayname = 'NEW NAME!'
        newclassget.save()
        
        # Retrieve all classes
        allclasses = Class.objects.all()
        self.assertTrue(allclasses)
        
        # Delete class
        newclassget.delete()
        
        # Delete school (and classes)
        School(schoolid = newschoolid).delete()
    
if __name__ == '__main__':
    unittest.main() # Run all tests