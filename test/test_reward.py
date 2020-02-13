import unittest
from test_setup import *

from wakemeup.models.program import Reward
    
class testReward(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.myreward1 = create_reward()
        self.myreward2 = create_reward(schoolyear=2000)
    
    def testCreateReward(self):
        self.assertTrue(self.myreward1.rewardid)

    def testGetReward(self):
        self.assertTrue(Reward.objects.all())
        self.assertTrue(Reward.objects.get(self.myreward1.rewardid))
        self.assertTrue(len(Reward.objects.get_rewards(schoolyear=2000)),1)
        
    def testUpdateReward(self):
        self.myreward1.rewardvalue=15000
        self.myreward1.save()
        self.myreward1 = refresh(self.myreward1)  # Refresh object
        self.assertEqual(self.myreward1.rewardvalue, 15000)

    def testDeleteReward(self):
        self.myreward1.delete()
        self.assertFalse(refresh(self.myreward1))

    def tearDown(self):        
        self.myreward1.delete()
        self.myreward2.delete()
        
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main() # Run all tests