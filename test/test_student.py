import test_setup
import unittest

from django.contrib.auth import get_user_model
from wakemeup.models.environment import Student, Class, School

class testStudent(unittest.TestCase):
    
    def setUp(self):
        global newuser
        global newclassid
        global newclass2id
        global newschoolid

        # Create new school
        newschool = School(None, 'My school','123 Fake Ln.','San Diego','CA')
        newschoolid = newschool.save()

        # Create new class        
        newclass = Class(None, newschoolid, 'My Class')
        newclassid = newclass.save()

        newclass2 = Class(None, newschoolid, 'My Class')
        newclass2id = newclass2.save()
        
        # Create new user
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'ST', firstname = 'Test', 
            lastname = 'Omoto', username = 'buffgecko', emailaddress = 'joe@smith.com', userrole = 'U'        
        )

    # Create new student
    def testStudent(self):
        self.assertEqual(newuser.firstname, 'Test')
        
        newstudent = Student(newuser.userid, newclassid)
        newstudent.save()

        newstudentget = Student.objects.get(newuser.userid)
        newstudentget.classid = newclass2id
        newstudentget.save()
        
        allstudents = Student.objects.all()
        for mystudent in allstudents:
            print (mystudent.studentuserid, mystudent.classid)

        newstudent.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests