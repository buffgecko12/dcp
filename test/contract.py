import test_setup
import unittest

from django.contrib.auth import get_user_model

from wakemeup.models.contracts import Contract
from wakemeup.models.environment import School, Class, Teacher

import json
from datetime import datetime

from psycopg2.extras import DateTimeTZRange

class testContract(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        global newschool
        global newclass
        global newclass2
        global newteacher
        global newcontract

        # Create environment
        newschool = School(None, 'My school','123 Fake Ln.','San Diego','CA')
        newschool.schoolid = newschool.save()
        
        newclass = Class(None, newschool.schoolid, 'My Class')
        newclass.classid = newclass.save()
        
        newclass2 = Class(None, newschool.schoolid, 'My Class 2')
        newclass2.classid = newclass2.save()

        # Teacher class info
        classinfo = json.dumps(
            { # classes info JSON
                "currentclasses" : [
                    {"classid" : newclass.classid},
                    {"classid" : newclass2.classid}
                ]
            }
        )
        
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher1', emailaddress = 'teacher@bufu.com'        
        )
        
        newteacher = Teacher(newuser.userid, classinfo)
        newteacherid = newteacher.save()

        # Create new contract
        newcontract = Contract(
            None, # contractid
            newclass.classid, 
            'G', # contracttype
            newteacher.teacheruserid, 
            DateTimeTZRange(datetime(2015, 1, 1, 0, 0, 0), datetime(2016, 1, 1, 0, 0, 0)), # Contract Valid Period
            None, # Guardian approval flag
            datetime(2015,7,1,0,0,0), # Revision approval ts
            None, # Student leader reqs
            None, # Teacher reqs 
            None, # Student reqs
            None, # Contract scan file
            None, # Contract approval TS
            None, # goal info (JSON)
            None, # reward info (JSON)
            None  # party info (JSON)
            )

        newcontract.contractid = newcontract.save()

    @classmethod
    def tearDownClass(self):
        newschool.delete()

    def testContract(self):
        pass
        
if __name__ == '__main__':
    unittest.main() # Run all tests