import test_setup
import unittest

from django.contrib.auth import get_user_model
from wakemeup.models.environment import Teacher, Class, School

import json

class testTeacher(unittest.TestCase):
    
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
            password = 'adminadmin', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher1', emailaddress = 'teacher@bufu.com'        
        )

    # Create new teacher
    def testTeacher(self):
        classinfo = json.dumps(
            { # classes info JSON
                "currentclasses" : [
                    {"classid" : newclassid},
                    {"classid" : newclass2id}
                ]
            }
        )
        
        newclassinfo = json.dumps(
                { # New classes info JSON
                "currentclasses" : [
                    {"classid" : newclassid},
                    {"classid" : newclass2id}
                ],
                "deletedclasses" : [newclassid]
            }
        )

        self.assertEqual(newuser.firstname, 'Teacher')
        
        newteacher = Teacher(newuser.userid, classinfo)
        newteacher.save()
 
        newteacherget = Teacher.objects.get(newuser.userid)
        newteacherget.classinfo = newclassinfo
        newteacherget.save()
         
        allteachers = Teacher.objects.all()
        for myteacher in allteachers:
            print (myteacher.teacheruserid, myteacher.classinfo)
 
        allclasses = newteacherget.get_classes()
        
        for myclass in allclasses:
            print (myclass.classid)
 
        newteacher.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests