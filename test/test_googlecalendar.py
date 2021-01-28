import unittest
# from test_env_setup import *
from test_setup import *
from UsefulFunctions.googleUtils import GoogleCalendar

TEST_GOOGLE_ACCOUNT = 'test@gmail.com'

class testGoogleCalendar(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Create service connections
        cls.gc_read = GoogleCalendar(permissions=['read'])
        cls.gc_write = GoogleCalendar(permissions=['write'])

        # Create calendar and event        
        cls.mycalendar1 = cls.gc_write.create_calendar(title='New Calendar 1', description='Some description', publicflag=True)
        cls.myevent1 = create_calendar_event(cls.gc_write, calendarid=cls.mycalendar1['id'], description='New event')
        create_calendar_event(cls.gc_write, calendarid=cls.mycalendar1['id'])

    def setUp(self):
        pass

    def ztestAddCalendar(self): # Disabled for now

        # Add calendar and verify
        self.gc_write.add_calendar(calendarid=TEST_GOOGLE_ACCOUNT)
        self.assertTrue(self.gc_read.get_calendar(calendarid=TEST_GOOGLE_ACCOUNT))

        # Delete calendar
        self.gc_write.delete_calendar(calendarid=TEST_GOOGLE_ACCOUNT)

    def testGetCalendar(self):
        mycalendar = self.gc_read.get_calendar(calendarid=self.mycalendar1['id'])
        self.assertTrue(mycalendar['id'], self.mycalendar1['id'])

        # Check default to user's primary calendar
        mycalendar = self.gc_read.get_calendar()
        self.assertTrue(mycalendar.get('primary'))

        self.assertTrue(self.gc_read.get_calendar(baseflag=True)) # Base
        self.assertFalse(self.gc_read.get_calendar(calendarid='dummy')) # Negative

        # Get calendar list
        self.assertGreater(len(self.gc_read.get_calendar_list()['items']), 1)

    def testWriteCalendar(self):

        # UPDATE
        mycalendar = self.gc_write.create_calendar(title='Test')
        mycalendar['description'] = 'New description'
        updated_calendar = self.gc_write.update_calendar(calendarid=mycalendar['id'], body=mycalendar, baseflag=True)

        self.assertTrue(updated_calendar['description'], 'New description')

        # ACL


        # DELETE
        # Try to create file with "read" authorization
        self.gc_read.delete_calendar(calendarid=self.mycalendar1['id'])
        self.assertTrue(self.gc_read.get_calendar(calendarid=self.mycalendar1['id'])) # Calendar should still exist

        # Delete user calendar and verify
        self.gc_write.delete_calendar(calendarid=self.mycalendar1['id'])
        self.assertFalse(self.gc_read.get_calendar(calendarid=self.mycalendar1['id'])) # User calendar gone
        self.assertTrue(self.gc_read.get_calendar(calendarid=self.mycalendar1['id'], baseflag=True)) # Base calendar still exists

        # Delete base calendar and verify
        self.gc_write.delete_calendar(calendarid=self.mycalendar1['id'], baseflag=True)
        self.assertFalse(self.gc_read.get_calendar(calendarid=self.mycalendar1['id'], baseflag=True)) # Base calendar gone

    def testCreateEvent(self):
        pass
        
    def testGetEvent(self):
        self.assertEqual(self.gc_read.get_event(calendarid=self.mycalendar1['id'], eventid=self.myevent1['id'])['description'], 'New event')
        self.assertTrue(self.gc_read.get_events(calendarid=self.mycalendar1['id']))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
        cls.gc_write.delete_calendar(calendarid=cls.mycalendar1['id'], baseflag=True)

if __name__ == '__main__':
    unittest.main() # Run all tests