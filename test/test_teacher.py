import test_setup
import unittest

from django.contrib.auth import get_user_model
from wakemeup.models.environment import Teacher, Class, School

import json

class testTeacher(unittest.TestCase):
    
    def setUp(self):
        global newuser
        global newclass
        global newclass2
        global newschool

        # Create new school
        newschool = School(None, 'My school','My abbreviation', '123 Fake Ln.','San Diego','CA')
        newschool.schoolid = newschool.save()

        # Create/save new class object
        newclass = Class(None, newschool.schoolid, 'My Class 1')
        newclass.classid = newclass.save()

        newclass2 = Class(None, newschool.schoolid, 'My Class 2')
        newclass2.classid = newclass2.save()

        try:
            check_existinguser = get_user_model().objects.get(username='teacher1')
            check_existinguser.delete()
        except:
            pass
        
        # Create new user
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher1', emailaddress = 'teacher@bufu.com', userrole = 'U',
            defaultsignaturescanfile = test_setup.readfile('test/img/samplesig1.png')

        )

    # Create new teacher
    def testTeacher(self):

        # Define class info        
        classinfo = json.dumps(
            { # classes info JSON
                "currentclasses" : [
                    {"classid" : newclass.classid},
                    {"classid" : newclass2.classid}
                ]
            }
        )
        
        # Remove "newclass"
        newclassinfo = json.dumps(
                { # New classes info JSON
                "currentclasses" : [
                    {"classid" : newclass2.classid}
                ],
                "deletedclasses" : [newclass.classid]
            }
        )

        # Check new user was created properly
        self.assertEqual(newuser.firstname, 'Teacher')

        # Verify newly created user created as a teacher
        newteacher = Teacher.objects.get(newuser.userid)
        self.assertTrue(newteacher)

        # Set teacher's initial class info
        newteacher.classinfo = classinfo
        newteacher.schoolid = newschool.schoolid
        myfirstname = newteacher.firstname
        newteacher.firstname = None # Firstname should not be overwritten with NULL
        newteacher.save()

        # Re-retrieve object and check that firstname was not changed
        newteacher = Teacher.objects.get(newuser.userid)
        self.assertEqual(myfirstname,newteacher.firstname)

        # Update more info
        newteacher.classinfo = newclassinfo
        mylastname = newteacher.lastname
        newteacher.lastname = 'New lastname'
        newteacher.save()

        # Re-retrieve object and check that firstname was not changed
        newteacher = Teacher.objects.get(newuser.userid)
        self.assertNotEqual(mylastname,newteacher.lastname)
        
        # Check helper methods
        allteachers = Teacher.objects.all()
        self.assertTrue(allteachers)

        allclasses = newteacher.get_classes()
        self.assertTrue(allclasses)
 
        newuser.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests