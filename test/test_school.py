import unittest
from test_setup import *
from datetime import date, timedelta
from lib.UsefulFunctions.dataUtils import * 

from wakemeup.models.school import School, SchoolReward

class testSchool(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.myreward1 = create_reward(schoolyear=2000)
        cls.myreward2 = create_reward()
        
    def setUp(self):
        self.myschool1 = create_school(schoolabbreviation = "MCHS")
        
        self.myschoolcalendar1 = create_school_calendar(schoolid=self.myschool1.schoolid,itemtype='SP',itemdate=date(2020,3,1))
        self.myschoolcalendar2 = create_school_calendar(schoolid=self.myschool1.schoolid,itemtype='EP',itemdate=date(2020,11,1))

        self.myschoolreward1 = create_school_reward(schoolid=self.myschool1.schoolid,rewardid=self.myreward1.rewardid, schoolyear=2000, rewardvalue=999)
        self.myschoolreward2 = create_school_reward(schoolid=self.myschool1.schoolid,rewardid=self.myreward2.rewardid)
    
    def testCreateSchool(self):
        self.assertTrue(self.myschool1.schoolid)
        self.assertEqual(self.myschool1.schoolabbreviation,'MCHS')

    def testGetSchool(self):
        self.assertTrue(School.objects.get(self.myschool1.schoolid))
        self.assertTrue(School.objects.all())
        self.assertTrue(School.objects.get_school_options(schoolid = self.myschool1.schoolid))
        
    def testUpdateSchool(self):    
        self.myschool1.schoolabbreviation = 'CMHS'
        self.myschool1.save()
        self.assertEqual(self.myschool1.schoolabbreviation,'CMHS')

    def testDeleteSchool(self):
        delete_school(self.myschool1)
        self.assertFalse(refresh(self.myschool1))

    def testCreateSchoolCalendar(self):
        pass

    def testGetSchoolCalendar(self):
        
        myschoolcalendar = SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid)
        
        self.assertTrue(SchoolCalendar.objects.get(calendaritemid=myschoolcalendar[0].calendaritemid))
        self.assertTrue(SchoolCalendar.objects.all())
        self.assertTrue(myschoolcalendar)

    def testUpdateSchoolCalendar(self):
        
        # Add rewards (bulk) and verify
        myschoolcalendar = SchoolCalendar(schoolid=self.myschool1.schoolid).save(calendarinfo=to_json(
            [
                {"itemdate":str(date.today()),"itemtype":"SP","itemnotes":"Start program notes","round":None},
                {"itemdate":str(date.today() + timedelta(days=10)),"itemtype":"CTE","itemnotes":"Contract Deadline 1","round":1},
                {"itemdate":str(date.today() + timedelta(days=70)),"itemtype":"CTE","itemnotes":"Contract Deadline 2","round":2},
                {"itemdate":str(date.today() + timedelta(days=120)),"itemtype":"EP","itemnotes":"End program notes","round":None},
            ]
        )
        )

        myschoolcalendar = SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid,itemtype='CTE',round=1)[0]
        self.assertTrue(myschoolcalendar)
        self.assertEqual(myschoolcalendar.itemnotes,'Contract Deadline 1')

    def testDeleteSchoolCalendar(self):
        
        # Check calendar items before
        self.assertTrue(SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid))

        # Delete and verify
        SchoolCalendar(schoolid=self.myschool1.schoolid).delete()
        self.assertFalse(SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid))

    def testCreateSchoolReward(self):
        pass

    def testGetSchoolReward(self):

        myreward = SchoolReward.objects.get(schoolid=self.myschool1.schoolid,rewardid=self.myreward1.rewardid)
        
        self.assertTrue(myreward)
        self.assertTrue(SchoolReward.objects.get_school_rewards(rewardid=self.myreward1.rewardid, schoolyear=2000))
        self.assertTrue(SchoolReward.objects.all())

        # Check reward values
        self.assertEqual(myreward.rewardvalue,999) # User-provided
        self.assertEqual(SchoolReward.objects.get(schoolid=self.myschool1.schoolid,rewardid=self.myreward2.rewardid).rewardvalue,5000) # Default

    def testUpdateSchoolReward(self):

        # Delete rewards and verify
        self.assertTrue(refresh(self.myschoolreward1))
        self.myschoolreward1.delete()
        self.assertFalse(refresh(self.myschoolreward1))
        
        # Add rewards (bulk) and verify
        myschoolrewards = SchoolReward(schoolid=self.myschool1.schoolid).save(rewardinfo=to_json(
            [
                {"rewardid":self.myreward1.rewardid,"rewardvalue":self.myreward1.rewardvalue},
                {"rewardid":self.myreward2.rewardid,"rewardvalue":self.myreward2.rewardvalue},
            ]
        )
        )

        myschoolreward = SchoolReward.objects.get(schoolid=self.myschool1.schoolid,rewardid=self.myreward1.rewardid)
        self.assertTrue(myschoolreward)
        self.assertEqual(myschoolreward.rewardvalue,self.myreward1.rewardvalue)

    def testCopySchoolReward(self):
        targetyear = self.myreward1.schoolyear + 1
        newreward = self.myreward1.copy(targetyear=targetyear, copyoptions={'copyschools':True})

        # Case 1 - Copy Reward and related school rewards
        # Check if all rewards are copied to new year
        self.assertEqual(Reward.objects.get(rewardid=newreward.rewardid).schoolyear, targetyear)
        self.assertEqual(SchoolReward.objects.get(schoolid=self.myschool1.schoolid, rewardid=newreward.rewardid).schoolyear, targetyear)

        # Delete copied school rewards
        for myschoolreward in SchoolReward.objects.get_school_rewards(rewardid=newreward.rewardid, schoolyear=None):
            myschoolreward.delete()
            
        # Case 2 - Copy school reward
        newschoolreward = self.myschoolreward1.copy(targetyear=targetyear)
        self.assertEqual(SchoolReward.objects.get(schoolid=newschoolreward.schoolid, rewardid=newschoolreward.rewardid).schoolyear, targetyear)
        newschoolreward.delete()
 
        # Case 3 - Copy school reward (without source reward already copied)
        newschoolreward = self.myschoolreward2.copy(targetyear=targetyear)
        self.assertEqual(SchoolReward.objects.get(schoolid=newschoolreward.schoolid, rewardid=newschoolreward.rewardid).schoolyear, targetyear)
        self.assertEqual(Reward.objects.get_rewards(sourcerewardid=self.myschoolreward2.rewardid, schoolyear=targetyear)[0].schoolyear, targetyear)
 
        # Case 4 - Make sure source reward does not get copied again if it has already been copied
        duplicatereward = self.myschoolreward2.copy(targetyear=targetyear)
        self.assertEqual(len(SchoolReward.objects.get_school_rewards(schoolid=newschoolreward.schoolid, sourcerewardid=self.myschoolreward2.rewardid, schoolyear=targetyear)), 1)
 
        newreward.delete()

    def testDeleteSchoolReward(self):
        
        # Check reward items before
        self.assertTrue(SchoolReward.objects.get_school_rewards(schoolid=self.myschool1.schoolid))

        # Delete and verify
        SchoolReward(schoolid=self.myschool1.schoolid).delete()
        self.assertFalse(SchoolReward.objects.get_school_rewards(schoolid=self.myschool1.schoolid))

    def tearDown(self):
        
        delete_school_calendar(self.myschool1)
        delete_school(self.myschool1)

        self.myschoolreward1.delete()
        self.myschoolreward2.delete()

    @classmethod
    def tearDownClass(cls):
        
        cls.myreward1.delete()
        cls.myreward2.delete()

if __name__ == '__main__':
    unittest.main() # Run all tests