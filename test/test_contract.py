import test_setup
import unittest

from django.contrib.auth import get_user_model

from wakemeup.models.contract import Contract, ContractGoal, ContractGoalReward, ContractParty, Reward
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
        global newuser
        global signaturefile

        global newreward

        # Prepare signature file        
        signaturefile = test_setup.readfile('test/img/sampleimg.jpg')

        # Create environment
        newschool = School(None, 'My school','My abbreviation', '123 Fake Ln.','San Diego','CA')
        newschool.schoolid = newschool.save()
        
        newclass = Class(None, newschool.schoolid, 'My Class 1')
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
        
        # Delete user if already exists
        try:
            checkuser = get_user_model().objects.get(username = 'teacher1')
            checkuser.delete()
        except:
            pass
        
        # Create new teacher
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher1', emailaddress = 'teacher@bufu.com', userrole = 'U'
        )
        
        newteacher = Teacher(teacheruserid=newuser.userid, schoolid=newschool.schoolid, classinfo=classinfo)
        newteacherid = newteacher.save()

        # Create new reward
        newreward = Reward(rewarddescription = 'Goal #101', rewardvalue = 755, createdbyuserid = newuser.userid)
        newreward.rewardid = newreward.save()

    # Re-create environment for each test case        
    def setUp(self):
        global newcontract

        # Contract goal info
        goalinfo = json.dumps(
            { # classes info JSON
                "currentgoals" : [
                    {"goalid" : None, "difficultylevel" : "M", "goaldescription" : "Some MEDIUM description", 
                     "rewardinfo": {"currentrewards" : [
                         {"rewardid" : 1},
                         {"rewardid" : 2},
                         ]}
                     },
                    {"goalid" : None, "difficultylevel" : "E", "goaldescription" : "Some easy goal", 
                     "rewardinfo": {"currentrewards" : [{"rewardid" : 1}]}},
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
            None, # classdisplayname
            'G', # contracttype
            newteacher.teacheruserid, 
            None, # teacherfirstname
            None, # teacherlastname
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
            partyinfo  # party info (JSON)
            )
                
        # Save new contract
        newcontract.contractid = newcontract.save()
        
        # Set contract status as "draft"
        newcontract.change_status('D')
        
    def testCreateContract(self):
        pass

    def testReward(self):
        newreward.rewarddescription = "New Description text"
        newreward.save()
        newrewardget = Reward.objects.get(rewardid=newreward.rewardid)
        self.assertNotEqual(newrewardget.rewarddescription,"Goal #102")

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

    # TO-DO: Fix the "approve" part
    def notestReviseContract(self):

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
        
        # Modify goal info
        newgoalinfo = json.dumps(
            { # classes info JSON
                "deletedgoals" : [3],
                "currentgoals" : [
                    {"goalid" : None, "difficultylevel" : "D", "goaldescription" : "Some new goal"},
                    {"goalid" : None, "difficultylevel" : "M", "goaldescription" : "Some NEW MEDIUM goal"},
                ]
            }
        )

        # Get all goals
        allgoals = ContractGoal.objects.all()
        self.assertIsNotNone(allgoals)

        # Get all medium goals
        getmediumgoals = ContractGoal.objects.get_contract_goals(difficultylevel = 'M')
        self.assertIsNotNone(getmediumgoals)
        
        # Check goal info was set properly
        mycontractgoal = ContractGoal.objects.get(contractid = newcontract.contractid, goalid = 1)
        self.assertEqual(mycontractgoal.goaldescription, "Some MEDIUM description")

        mycontractgoal = ContractGoal.objects.get(contractid = newcontract.contractid, goalid = 2)
        self.assertEqual(mycontractgoal.difficultylevel, "E")

        # Update existing goal and verify save
        mycontractgoal.difficultylevel = "D"
        mycontractgoal.save()
        mycontractgoal = ContractGoal.objects.get(contractid = newcontract.contractid, goalid = 2)
        self.assertEqual(mycontractgoal.difficultylevel, "D")

        # Create new goal
        newcontractgoal = ContractGoal(newcontract.contractid, None, 'M', 'Manual goal', None, None, 
                                       json.dumps({"currentrewards" : [{"rewardid" : newreward.rewardid}]})
                                   )

        newcontractgoalid = newcontractgoal.save()
        newcontractgoal = ContractGoal.objects.get(contractid = newcontract.contractid, goalid = newcontractgoalid)
        self.assertEqual(newcontractgoal.goaldescription,"Manual goal")
                
#         mycontractgoalreward = ContractGoalReward.objects.get(contractid = newcontractgoal.contractid, goalid=newcontractgoal.goalid, rewardid=newrewardid)
#         self.assertEqual(mycontractgoalreward.rewardvalue,50)

        # Check delete goal
        mycontractgoal.delete()
        mycontractgoal = ContractGoal.objects.get(contractid = newcontract.contractid, goalid = 2)
        self.assertIsNone(mycontractgoal)        
        
        # Check reward info set properly
        mycontractgoalreward = ContractGoalReward.objects.get(contractid = newcontract.contractid, goalid=3, rewardid=newreward.rewardid)
        self.assertEqual(mycontractgoalreward.rewarddescription,"Goal #101")

        mycontractgoalreward = ContractGoalReward.objects.get(contractid = newcontract.contractid, goalid=3, rewardid=newreward.rewardid)
        self.assertEqual(mycontractgoalreward.rewardvalue,755)

        # Create new reward
        newcontractgoalreward = ContractGoalReward(newcontract.contractid, 1, newreward.rewardid)
        newcontractgoalrewardid = newcontractgoalreward.save()
        newcontractgoalreward = ContractGoalReward.objects.get(newcontract.contractid, 1, newreward.rewardid)
        self.assertEqual(newcontractgoalreward.rewarddescription,'Goal #101')

        # Check delete reward
        mycontractgoalreward.delete()
        mycontractgoalreward = ContractGoalReward.objects.get(contractid = newcontract.contractid, goalid=3, rewardid=newreward.rewardid)
        self.assertIsNone(mycontractgoalreward)

    def testContractGoalRewards(self):
        
        allrewards = ContractGoalReward.objects.all()

        # Get newly created reward
        getreward = ContractGoalReward.objects.get(contractid = newcontract.contractid, goalid = 1, rewardid = 1)
        self.assertIsNotNone(getreward)

        # Modify reward info
        newrewardinfo = json.dumps(
            { # classes info JSON
                "deletedrewards" : [1],
                "currentrewards" : [
                    {"rewardid" : 1},
                    {"rewardid" : 2},
                ]
            }
        )

#        ContractGoalReward.objects.modify_contract_rewards(newcontract.contractid, newrewardinfo)

        # Verify updated reward info
#         getnewreward = ContractGoalReward.objects.get(contractid = newcontract.contractid, goalid = 1, rewardid = 2)
#         self.assertEqual(getnewreward.rewarddescription,"Some NEW MEDIUM reward")

    def testContractParties(self):        
        # Get all parties
        allparties = ContractParty.objects.all()
        self.assertIsNotNone(allparties)
        
        # Get single party
        getparty = ContractParty.objects.get(newcontract.contractid,2)
        self.assertIsNotNone(getparty)
        
        # Get all parties for given contract
        getparties = ContractParty.objects.get_contract_parties(newcontract.contractid, None, None)
        self.assertIsNotNone(getparties)

        # Check backup leader
        getbackupleader = ContractParty.objects.get_contract_parties(newcontract.contractid, None, 'BL')
        self.assertIsNotNone(getbackupleader)
        
        # Modify contract parties
        newpartyinfo = json.dumps(
            { # parties info JSON
                "deletedparties" : [1],
                "currentparties" : [
                    {"partyuserid" : 3, "contractrole" : "PT"},
                ]
            }
        )
        ContractParty.objects.modify_contract_parties(newcontract.contractid, newpartyinfo)

        # Verify party was deleted
        getnewparty = ContractParty.objects.get(newcontract.contractid,1)
        self.assertIsNone(getnewparty)
        
        # Verify contract role was changed
        getbackupleader = ContractParty.objects.get_contract_parties(newcontract.contractid, None, 'BL')
        self.assertFalse(getbackupleader)

        # Set party attributes
        getparty.partylogonuserid = 1
        getparty.partyapprovalsignature = signaturefile
        getparty.partyapprovalts = datetime.utcnow()

        # Setup remaining parties
        getparty3 = ContractParty.objects.get(newcontract.contractid,partyuserid=3)
        getparty3.partylogonuserid = 1

        getparty4 = ContractParty.objects.get(newcontract.contractid,partyuserid=4)
        getparty4.partylogonuserid = 1

        # Approve contract (2 out of required 3 users)
        getparty.approve_contract() # Userid = 2
        getparty3.approve_contract()
        
        # Check contract has not been approved yet (2 out of required 3 have approved)
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNone(newcontractget.contractapprovalts)

        # Submit final approval (3 out of 3)
        getparty4.approve_contract()

        # Check contract is approved
        newcontractget = Contract.objects.get(newcontract.contractid)
        self.assertIsNotNone(newcontractget.contractapprovalts)

    def tearDown(self):
        
        # Set back to draft and delete
        newcontract.change_status('D')
        newcontract.delete()

    @classmethod
    def tearDownClass(self):
        newschool.delete()
        newuser.delete()
        newreward.delete()
        
if __name__ == '__main__':
    unittest.main() # Run all tests