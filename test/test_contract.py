import test_setup
import unittest

from django.contrib.auth import get_user_model

from wakemeup.models.contracts import Contract
from wakemeup.models.environment import School, Class, Teacher

import json
from datetime import datetime, timedelta

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

        # Contract goal info
        goalinfo = json.dumps(
            { # classes info JSON
                "currentgoals" : [
                    {"goalid" : None, "difficultylevel" : "M", "goaldescription" : "Some yummy description", "achievedflag" : None, "acceptedflag" : True},
                ]
            }
        )

        # Contract reward info
        rewardinfo = json.dumps(
            {
                "currentrewards" : [
                    {"rewardid" : None, "difficultylevel" : "M", "rewarddescription" : "Some great description"}
                ]
            }    
        )

        # Contract party info
        partyinfo = json.dumps(
            {
                "currentparties" : [
                    {"partyuserid": 1,"contractrole": "MR"},
                    {"partyuserid": 2,"contractrole": "PL"},
                    {"partyuserid": 3,"contractrole": "BL"},
                    {"partyuserid": 4,"contractrole": "PT"}
                ]
            }
        )

        # Create new contract
        newcontract = Contract(
            None, # contractid
            newclass.classid, 
            'G', # contracttype
            newteacher.teacheruserid, 
            DateTimeTZRange(datetime(2015, 1, 1, 0, 0, 0), datetime(2016, 1, 1, 0, 0, 0)), # Contract Valid Period
            False, # Guardian approval flag
            datetime.now() + timedelta(days=10), # Revision deadline ts
            None, # Revision description
            None, # Revision approval TS
            'Don''t do dees!', # Student leader reqs
            'Great teacher reqs', # Teacher reqs 
            'Some student reqs', # Student reqs
            None, # Contract scan file
            None, # Contract approval TS
            goalinfo, # goal info (JSON)
            rewardinfo, # reward info (JSON)
            partyinfo  # party info (JSON)
            )

        newcontract.contractid = newcontract.save()

        # Approve contract
        newcontract.approve(1,'C',None,datetime.now(),1)
        newcontract.approve(2,'C',None,datetime.now(),1)
        newcontract.approve(3,'C',None,datetime.now(),1)
        newcontract.approve(4,'C',None,datetime.now(),1)

        # Revise contract
        newcontract.revisiondescription = 'My revision description mang!'
        newcontract.revise()

        # Approve revision
        newcontract.approve(1,'R',None,datetime.now(),1)
        newcontract.approve(2,'R',None,datetime.now(),1)

    @classmethod
    def tearDownClass(self):
        newschool.delete()

    def testContract(self):
        pass
        
if __name__ == '__main__':
    unittest.main() # Run all tests