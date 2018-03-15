import test_setup
import unittest

from django.contrib.auth import get_user_model
from users.models import UserReputationEvent

class testUserReputation(unittest.TestCase):
    
    def setUp(self):
        global newuser 
        
        newuser = get_user_model().objects.create_user(
            password = 'adminadmin', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher2', emailaddress = 'teacher2@bufu.com'        
        )
        
    def testUserReputationEvent(self):
        
        # Create new reputation event
        newevent = UserReputationEvent(None, newuser.userid, 'BP', None, 10, 1)
        neweventid = newevent.save()
                
        self.assertIsNotNone(neweventid)

        # Get event
        neweventget = UserReputationEvent.objects.get(neweventid)
        neweventget.pointvalue = 100

        neweventget.save()
        
        self.assertEqual(neweventget.eventtype, 'BP')        
        self.assertEqual(neweventget.pointvalue, 100)
                
        # Get all events
        allevents = UserReputationEvent.objects.all()
         
        for myevent in allevents:
            print(myevent.eventid)
        
        neweventget.delete()
        
if __name__ == '__main__':
    unittest.main() # Run all tests