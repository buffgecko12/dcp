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
        newschool = School(None, 'My school','123 Fake Ln.','San Diego','CA')
        newschool.schoolid = newschool.save()

        # Create/save new class object
        newclass = Class(None, newschool.schoolid, 'My Class 1')
        newclass.classid = newclass.save()

        newclass2 = Class(None, newschool.schoolid, 'My Class 2')
        newclass2.classid = newclass2.save()
        
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
        
        newclassinfo = json.dumps(
                { # New classes info JSON
                "currentclasses" : [
                    {"classid" : newclass.classid},
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
        newteacher.save()

        # Update teacher's class info 
        newteacherget = Teacher.objects.get(newuser.userid)
        newteacherget.classinfo = newclassinfo
        newteacherget.save()

        # Check helper methods
        allteachers = Teacher.objects.all()
        self.assertTrue(allteachers)

        allclasses = newteacherget.get_classes()
        self.assertTrue(allclasses)
 
        newuser.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests