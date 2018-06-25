import test_setup
import unittest

from django.contrib.auth import get_user_model
from wakemeup.models.environment import Student, Class, School

class testStudent(unittest.TestCase):

    # Setup test environment (run once)
    @classmethod    
    def setUpClass(self):
        global newuser
        global newclass
        global newclass2
        global newschool

        # Create new school
        newschool = School(None, 'My school','123 Fake Ln.','San Diego','CA')
        newschool.schoolid = newschool.save()

        # Create/save new class object
        newclass = Class(None, newschool.schoolid, 'My Class 1')
        newclass.classid = newclass.save()

        newclass2 = Class(None, newschool.schoolid, 'My Class 2')
        newclass2.classid = newclass2.save()
        
        # Create new user (student)
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'ST', firstname = 'Test', 
            lastname = 'Omoto', username = 'buffgecko_test', emailaddress = 'new_user@smith.com', userrole = 'U'        
        )

    # Create new student
    def testStudent(self):
        # Check to make sure new user was created
        self.assertEqual(newuser.firstname, 'Test')

        # Check to make sure new student is not assigned to a class (i.e. classid = 0)
        newstudent_initial = Student.objects.get(newuser.userid)
        self.assertEqual(newstudent_initial.classid,0)

        # Assign student to new class
        newstudent = Student(newuser.userid, newclass.classid)
        newstudent.save()
        
        newstudentget = Student.objects.get(newuser.userid)
        self.assertEqual(newstudentget.classid, newclass.classid) # Check new classid was updated

        # Change student's class
        newstudentget.classid = newclass2.classid
        newstudentget.save()

        newstudentget2 = Student.objects.get(newuser.userid)
        self.assertEqual(newstudentget2.classid,newclass2.classid)

        # Check "getclass" method for updated classes
        students_class = Student.objects.getclass(newclass2.classid)
        self.assertTrue(students_class)
        
        students_class = Student.objects.getclass(newclass.classid)
        self.assertFalse(students_class)

        # Check "all" method
        allstudents = Student.objects.all()
        self.assertTrue(allstudents)

    @classmethod
    def tearDownClass(self):
        newuser.delete()
        newclass.delete()
        newclass2.delete()
        newschool.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests