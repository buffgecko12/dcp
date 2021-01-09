import test_env_setup
import unittest

from django.contrib.auth import get_user_model
from user.models.user import UserReputationEvent, UserBadge, UserNotification
from wakemeup.tables import UserReputationEventsTable

class testUserReputation(unittest.TestCase):
    
    global refresh_user;
    
    def refresh_user(self):
        return get_user_model().objects.get(userid=self.userid)
    
    def setUp(self):
        
        # Delete user (if exists)
        try:
            existinguser = get_user_model().objects.get(username='teacher2')
            existinguser.delete()
        except:
            pass
        
        global newuser 
        
        newuser = get_user_model().objects.create_user(
            password = 'testpass', usertype = 'TR', firstname = 'Teacher', 
            lastname = 'Isgood', username = 'teacher2', emailaddress = 'teacher2@mail.com'
        )
        
        
    def testUserReputationEvent(self):
        # Lookup user again to get all DB attributes
        myuser = refresh_user(newuser)

        # Verify user has default reputation/badge info (newuser = "rookie" badge and 5 reputation)
        myreputationevents = UserReputationEvent.objects.get_events(userid = myuser.userid)
        mybadges = UserBadge.objects.get_badges(userid = myuser.userid, badgeid=1) # rookie badge

        self.assertEqual(myuser.reputationvalue,5)
        self.assertIsNotNone(myreputationevents)        
        self.assertIsNotNone(mybadges)

        # Trigger some events for new user
        myuser.add_event(eventid=2001) # Create new account

        # Verify reputation / badges created
        myuser = refresh_user(myuser)
        myuserbadge = UserBadge.objects.get(userid=myuser.userid,badgeid=1)
        myreputationevents = UserReputationEvent.objects.get_events(userid=myuser.userid)
        myreputationeventstable = UserReputationEventsTable(UserReputationEvent.objects.get_events(userid=myuser.userid))

        self.assertNotEqual(myuser.reputationvalue,0)
        self.assertIsNotNone(myuserbadge)
        self.assertIsNotNone(myreputationevents)
        self.assertTrue(len(myreputationeventstable.rows))
        
        # Create enough events to trigger "junior user" threshold badge
        myuser.add_event(eventid=2005) # Difficult goal
        myuser.add_event(eventid=2007) # Top performer

        myuser = refresh_user(myuser)
        mynewbadge = UserBadge.objects.get(userid=myuser.userid,badgeid=8) # Difficult goal 
        self.assertIsNotNone(mynewbadge)

        mynewbadge = UserBadge.objects.get(userid=myuser.userid,badgeid=10) # Top performer 
        self.assertIsNotNone(mynewbadge)

        mynewbadge = UserBadge.objects.get(userid=myuser.userid,badgeid=2) # 100+ reputation points
        self.assertGreater(myuser.reputationvalue, 100)
        self.assertIsNotNone(mynewbadge)

    def testUserNotification(self):
        # Lookup user again to get all DB attributes
        myuser = refresh_user(newuser)

        # Verify new user has a notification already
        mynotifications = UserNotification.objects.get_notifications(userid = myuser.userid)
        self.assertIsNotNone(mynotifications)

        # Create new notification
        myuser.add_notification(notificationid=1001) # Create new alert (reputation points)

        # Verify user has notifications
        mynotifications = UserNotification.objects.get_notifications(userid = myuser.userid)
        allnotifications = UserNotification.objects.all()
        
        self.assertIsNotNone(mynotifications)
        self.assertIsNotNone(allnotifications)
                
    def testUserReputationNotification(self):
        # Lookup user again to get all DB attributes
        myuser = refresh_user(newuser)

        # Verify last seen TS is not yet set
        self.assertIsNone(myuser.reputationvaluelastseents)

        # Verify new user has a "new reputation points" notification already
        mynotifications = UserNotification.objects.get_notifications(userid = myuser.userid, sourceeventid=1001)
        self.assertIsNotNone(mynotifications)

        opennotifications = myuser.manage_display_info(actiontype='getuserdisplayinfo')['opennotificationsflag']
        self.assertTrue(opennotifications)

        # Look up single notification by id
        mynotificationid = mynotifications[0].notificationid
        mynotification = UserNotification.objects.get(mynotificationid)
        self.assertIsNotNone(mynotification)

        # Mark reputation notification as "seen"
        myuser.manage_display_info(actiontype='clearnewrepnotification')
        
        # Verify that "last seen TS" has been set
        myuser = refresh_user(myuser)
        self.assertIsNotNone(myuser.reputationvaluelastseents)
        
        # Verify "reputation" notifications are gone
        mynotifications = UserNotification.objects.get_notifications(userid = myuser.userid, sourceeventid=2001)
        self.assertFalse(mynotifications)

        # Create new event that adds reputation points
        myuser.add_event(eventid=2001) # new account event (5 points)

        # Verify point delta
        pointdelta = myuser.manage_display_info(actiontype='getuserdisplayinfo')['reputationvaluedelta']
        self.assertEqual(pointdelta,5)

        # Mark reputation notification as "seen" and check pointdelta again
        myuser.manage_display_info(actiontype='clearnewrepnotification')
         
        pointdelta = myuser.manage_display_info(actiontype='getuserdisplayinfo')['reputationvaluedelta']
        self.assertEqual(pointdelta,0)

    def testUserBadges(self):

        def get_badges(userid, badgeid):
            return UserBadge.objects.get_badges(userid = userid, badgeid=badgeid)
            
        myuser = newuser
        
        # Check "submit feedback" badges
        self.assertFalse(get_badges(myuser.userid,19)) # bronze
        myuser.add_event(eventid=2013) # submit feedback
        self.assertTrue(get_badges(myuser.userid,19))

        ''' TO-DO: Add test cases
        - accept three goals (2002) --> bronze + silver badges
        - evaluate contract (2015) --> reputation
        - send 1/10/50 contracts (2014) --> badges + reputation
        - complete 3/10 goals (2) --> badges + reputation
        '''
        
if __name__ == '__main__':
    unittest.main() # Run all tests
