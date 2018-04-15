import test_setup
import unittest

from django.contrib.auth import get_user_model

from wakemeup.models.contracts import Contract, ContractGoal, ContractReward
from wakemeup.models.environment import School, Class, Teacher

import json
from datetime import datetime, timedelta

from psycopg2.extras import DateTimeTZRange

class testContracts(unittest.TestCase):

    # Create main test environment
    @classmethod
    def setUpClass(self):
        global newschool
        global newclass
        global newteacher

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
            lastname = 'Isgood', username = 'teacher1', emailaddress = 'teacher@bufu.com', userrole = 'U'
        )
        
        newteacher = Teacher(newuser.userid, classinfo)
        newteacherid = newteacher.save()

    # Re-create environment for each test case        
    def setUp(self):
        global newcontract

        # Contract goal info
        goalinfo = json.dumps(
            { # classes info JSON
                "currentgoals" : [
                    {"goalid" : None, "difficultylevel" : "M", "goaldescription" : "Some MEDIUM description"},
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
            None, # Contract status ("draft")
            goalinfo, # goal info (JSON)
            rewardinfo, # reward info (JSON)
            partyinfo  # party info (JSON)
            )
                
        # Save new contract
        newcontract.contractid = newcontract.save()
        
        # Set contract status as "draft"
        newcontract.change_status('D')
        
    def testCreateContract(self):
        pass

    def testGetContract(self):
        newcontractget = Contract.objects.get(newcontract.contractid)

        self.assertEqual(newcontractget.studentrequirements,newcontract.studentrequirements)

        # Check status is "draft")
        self.assertEqual(newcontractget.contractstatus,'D')

        # Set contract as pending (i.e. awaiting approval)        
        newcontractget.change_status('P')
        newcontractget = Contract.objects.get(newcontractget.contractid)

        # Check status is changed to "pending")
        self.assertEqual(newcontractget.contractstatus,'P')

    def testApproveContract(self):

        # Approve 3/4 required
        newcontract.approve(1,'C',None,datetime.now(),1)
        newcontract.approve(2,'C',None,datetime.now(),1)
        newcontract.approve(3,'C',None,datetime.now(),1)

        # Check approvalTS is still not set
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNone(newcontractget.contractapprovalts)

        # Submit final approval
        newcontract.approve(4,'C',None,datetime.now(),1)

        # Check approval TS is set
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNotNone(newcontractget.contractapprovalts)

    def testReviseContract(self):

        newcontract.revisiondescription = 'My revision description mang!'
        newcontract.revise()

        # Check revision approval TS is not set
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNone(newcontractget.revisionapprovalts)

        # Approve revision (1/2 required users)
        newcontract.approve(1,'R',None,datetime.now(),1)
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNone(newcontractget.revisionapprovalts)

        # Approve revision (2/2 required users)
        newcontract.approve(2,'R',None,datetime.now(),1)
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNotNone(newcontractget.revisionapprovalts)

    def testContractGoals(self):
        
        allgoals = ContractGoal.objects.all()

        # Get newly created goal
        getgoal = ContractGoal.objects.get(newcontract.contractid,1)
        self.assertIsNotNone(getgoal)

        # Get all medium goals
        getmediumgoals = ContractGoal.objects.get_contract_goals(difficultylevel = 'M')
        self.assertIsNotNone(getmediumgoals)
        
        # Accept goal
        getgoal.accept()
        getgoalagain = ContractGoal.objects.get(newcontract.contractid,1)
        self.assertTrue(getgoalagain.acceptedflag)

        # Modify goal info
        newgoalinfo = json.dumps(
            { # classes info JSON
                "deletedgoals" : [1],
                "currentgoals" : [
                    {"goalid" : None, "difficultylevel" : "D", "goaldescription" : "Some new goal"},
                    {"goalid" : None, "difficultylevel" : "M", "goaldescription" : "Some NEW MEDIUM goal"},
                ]
            }
        )

        ContractGoal.objects.modify_goals(newcontract.contractid, newgoalinfo)

        # Verify updated goal info
        getnewgoal = ContractGoal.objects.get(newcontract.contractid, 2)
        self.assertEqual(getnewgoal.goaldescription,"Some NEW MEDIUM goal")

    def testContractRewards(self):
        
        allrewards = ContractReward.objects.all()

        # Get newly created reward
        getreward = ContractReward.objects.get(newcontract.contractid,1)
        self.assertIsNotNone(getreward)

        # Get all medium rewards
        getmediumrewards = ContractReward.objects.get_contract_rewards(difficultylevel = 'M')
        self.assertIsNotNone(getmediumrewards)

        # Modify reward info
        newrewardinfo = json.dumps(
            { # classes info JSON
                "deletedrewards" : [1],
                "currentrewards" : [
                    {"rewardid" : None, "difficultylevel" : "D", "rewarddescription" : "Some new reward"},
                    {"rewardid" : None, "difficultylevel" : "M", "rewarddescription" : "Some NEW MEDIUM reward"},
                ]
            }
        )

        ContractReward.objects.modify_rewards(newcontract.contractid, newrewardinfo)

        # Verify updated reward info
        getnewreward = ContractReward.objects.get(newcontract.contractid,2)
        self.assertEqual(getnewreward.rewarddescription,"Some NEW MEDIUM reward")

    @classmethod
    def tearDownClass(self):
        newschool.delete()
        
if __name__ == '__main__':
    unittest.main() # Run all tests