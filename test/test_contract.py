import unittest
from test_setup import *
from wakemeup.models.program import *
from wakemeup.models.environment import *
from lib.UsefulFunctions.miscUtils import get_school_year
from lib.UsefulFunctions.dataUtils import * 

DEFAULT_SCHOOL_YEAR = get_school_year()

class testContracts(unittest.TestCase):

    # Create main test environment
    @classmethod
    def setUpClass(cls):
        cls.myschool = create_school()
        cls.myclass1 = create_class(schoolid=cls.myschool.schoolid)
        cls.myclass2 = create_class(schoolid=cls.myschool.schoolid)
        cls.myclass3 = create_class(schoolid=cls.myschool.schoolid)
        cls.myteacher1 = create_user(usertype='TR',emailaddress='test1@mail.com')
        cls.myteacher2 = create_user(usertype='TR')

        # Associate classes with teachers
        create_teacher_class(cls.myteacher1.userid, cls.myclass1.classid)
        TeacherClass(teacheruserid=cls.myteacher2.userid,classid=None).save(classidlist=[cls.myclass2.classid, cls.myclass3.classid])

        # Create contract file
        cls.myfile = create_file(filename='contractscan',fileextension='pdf',filetype='application/pdf',filedescription='Class 1 - Contract',filesource='DB',filecategory='CT')

        cls.myreward1 = create_reward(rewarddisplayname='My Reward 1')
        cls.myreward2 = create_reward(rewarddisplayname='My Reward 2',rewardvalue=20000)
        
    # Re-create environment for each test case        
    def setUp(self):

        # Contract party info
        partyinfo = to_json([
            {"teacheruserid":self.myteacher1.userid,"classid":self.myclass1.classid,"numparticipants":10,"numwinners":5},
            {"teacheruserid":self.myteacher2.userid,"classid":self.myclass2.classid,"numparticipants":20,"numwinners":7}
        ])

        # Create contract
        self.mycontract1 = create_contract(contractname='Reading activity',partyinfo=partyinfo)
        self.mycontract2 = create_contract(contractname='Reading activity 2',partyinfo=partyinfo,schoolyear=2000)

        # Contract parties / reward
        self.mycontractparty1 = create_contract_party(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher2.userid,classid=self.myclass3.classid)
        self.mycontractpartyreward1 = create_contract_party_reward(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher1.userid,classid=self.myclass1.classid,rewardid=self.myreward1.rewardid)
        self.mycontractpartyreward2 = create_contract_party_reward(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher2.userid,classid=self.myclass3.classid,rewardid=self.myreward2.rewardid,quantity=10)

        # Associate file with contract 1
        self.myfile.contractid = self.mycontract1.contractid
        self.myfile.save()
        
    ### CONTRACTS ###
    def testCreateContract(self):
        self.assertTrue(self.mycontract1.contractid)

    def testGetContract(self):
        self.assertIsNotNone(Contract.objects.get(contractid=self.mycontract1.contractid))
        self.assertEqual(len(Contract.objects.get_contracts(schoolyear=2000)),1) # specific school year
        self.assertEqual(len(Contract.objects.get_contracts(schoolyear=DEFAULT_SCHOOL_YEAR)),1) # default school year
        self.assertEqual(len(Contract.objects.get_contracts(teacheruserid=self.myteacher1.userid)),2) # teacher (positive) - 2 contracts
        self.assertFalse(Contract.objects.get_contracts(teacheruserid=-1)) # teacher (negative)

    def testDeleteContract(self):
        self.mycontract2.delete()
        self.assertFalse(refresh(self.mycontract2))

    def testContractFile(self):
        self.assertTrue(File.objects.get_files(contractid=self.mycontract1.contractid)) # positive
        self.assertFalse(File.objects.get_files(contractid=self.mycontract2.contractid)) # negative

    ### CONTRACT PARTIES ###
    def testCreateContractParty(self):
        pass
    
    def testGetContractParty(self):
        self.assertIsNotNone(ContractParty.objects.all()) # all parties
        self.assertIsNotNone(ContractParty.objects.get(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher1.userid,classid=self.myclass1.classid)) # specific party
        self.assertEqual(len(ContractParty.objects.get_contract_parties(contractid=self.mycontract1.contractid)),3) # a specific contract's parties (3)
        self.assertEqual(len(ContractParty.objects.get_contract_parties(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher2.userid)),2) # a teacher's parties (2) for a specific contract

        # Check that expected users are all included in contract users
#         self.assertTrue(set([2,3,4]) <= set(contractusers)) # regular users 

    def testUpdateContractParty(self):
        
        # Update values
        self.mycontractparty1.numwinners = 4
        self.mycontractparty1.save()

        # Test values
        self.mycontractparty1 = refresh(self.mycontractparty1)
        self.assertTrue(self.mycontractparty1.numwinners,4)
        self.assertIsNone(self.mycontractparty1.numparticipants)

    def testdeleteContractParty(self):
        
        # Check parties exist
        self.assertTrue(ContractParty.objects.get_contract_parties(teacheruserid=self.myteacher2.userid))

        # Delete parties        
        for mycontract in ContractParty.objects.get_contract_parties(teacheruserid=self.myteacher2.userid):
            mycontract.delete()
            
        # Check appropriate parties deleted
        self.assertFalse(ContractParty.objects.get_contract_parties(teacheruserid=self.myteacher2.userid))
        self.assertTrue(ContractParty.objects.get_contract_parties(teacheruserid=self.myteacher1.userid))

    def testCreateContractPartyReward(self):
        pass
    
    def testGetContractPartyReward(self):
        self.assertIsNotNone(ContractPartyReward.objects.all())
        self.assertIsNotNone(ContractPartyReward.objects.get(contractid=self.mycontract1.contractid,teacheruserid=self.myteacher1.userid,classid=self.myclass1.classid,rewardid=self.myreward1.rewardid))
        self.assertTrue(len(ContractPartyReward.objects.get_contract_party_rewards(contractid=self.mycontract1.contractid)),2) # check for contract rewards 
        self.assertTrue(len(ContractPartyReward.objects.get_contract_party_rewards(classid=self.myclass3.classid)),1) # check for class's total rewards 

    def testDeleteContractPartyReward(self):
        
        # Check party rewards exist
        self.assertTrue(ContractPartyReward.objects.get_contract_party_rewards(teacheruserid=self.myteacher1.userid))

        # Delete parties        
        for mycontractpartyreward in ContractPartyReward.objects.get_contract_party_rewards(teacheruserid=self.myteacher1.userid):
            mycontractpartyreward.delete()
            
        # Check appropriate parties deleted
        self.assertFalse(ContractPartyReward.objects.get_contract_party_rewards(teacheruserid=self.myteacher1.userid))
        self.assertTrue(ContractPartyReward.objects.get_contract_party_rewards(teacheruserid=self.myteacher2.userid))

    def tearDown(self):
        self.mycontract1.delete() # Deletes any related contract info (i.e. parties / rewards)
        self.mycontract2.delete()

    @classmethod
    def tearDownClass(self):
        delete_school(self.myschool)
        self.myclass1.delete() # Deletes any related teacher-class associations as well
        self.myclass2.delete()
        self.myclass3.delete()
        self.myteacher1.delete()
        self.myteacher2.delete()
        self.myfile.delete()
        
if __name__ == '__main__':
    unittest.main() # Run all tests