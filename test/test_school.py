import unittest
from test_setup import *
import json

from wakemeup.models.school import School, SchoolReward

class testSchool(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.myreward1 = create_reward()
        cls.myreward2 = create_reward()
        
    def setUp(self):
        self.myschool1 = create_school(schoolabbreviation = "MCHS")
        
        self.myschoolcalendar1 = create_school_calendar(schoolid=self.myschool1.schoolid,itemtype='SP',itemdate=date(2020,3,1))
        self.myschoolcalendar2 = create_school_calendar(schoolid=self.myschool1.schoolid,itemtype='EP',itemdate=date(2020,11,1))

        self.myschoolreward1 = create_school_reward(schoolid=self.myschool1.schoolid,rewardid=self.myreward1.rewardid,rewardvalue=999)
        self.myschoolreward2 = create_school_reward(schoolid=self.myschool1.schoolid,rewardid=self.myreward2.rewardid)
    
    def testCreateSchool(self):
        self.assertTrue(self.myschool1.schoolid)
        self.assertEqual(self.myschool1.schoolabbreviation,'MCHS')

    def testGetSchool(self):
        self.assertTrue(School.objects.get(self.myschool1.schoolid))
        self.assertTrue(School.objects.all())
        self.assertTrue(School.objects.school_choices(schoolid = self.myschool1.schoolid))
        
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
        pass

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
        self.assertTrue(SchoolReward.objects.get_school_rewards(rewardid=self.myreward1.rewardid))
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
        myschoolrewards = SchoolReward(schoolid=self.myschool1.schoolid).save(rewardinfo=json.dumps(
            [
                {"rewardid":self.myreward1.rewardid,"rewardvalue":self.myreward1.rewardvalue},
                {"rewardid":self.myreward2.rewardid,"rewardvalue":self.myreward2.rewardvalue},
            ]
        )
        )

        myschoolreward = SchoolReward.objects.get(schoolid=self.myschool1.schoolid,rewardid=self.myreward1.rewardid)
        self.assertTrue(myschoolreward)
        self.assertEqual(myschoolreward.rewardvalue,self.myreward1.rewardvalue)

    def testDeleteSchoolReward(self):
        
        # Check calendar items before
        self.assertTrue(SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid))

        # Delete and verify
        SchoolCalendar(schoolid=self.myschool1.schoolid).delete()
        self.assertFalse(SchoolCalendar.objects.get_school_calendars(schoolid=self.myschool1.schoolid))

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