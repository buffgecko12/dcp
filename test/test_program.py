import unittest
import itertools
from test_setup import *
from lib.UsefulFunctions.dataUtils import * 

from django.contrib.auth import get_user_model

class testProgram(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):

        # Google Drive
        cls.gd = GoogleDrive(permissions=['write'])
        cls.gc = GoogleCalendar(permissions=['write'])

        # Create school
        cls.myschool = create_school()

        # Define programs at each school
        cls.myprogram1 = create_program(schoolyear=DEFAULT_SCHOOL_YEAR, schoolid=cls.myschool.schoolid, gd=cls.gd, gc=cls.gc)
        cls.myprogram2 = create_program(schoolyear=2019, schoolid=cls.myschool.schoolid, gd="default", gc="default")
 
        # Create users
        cls.myuser_teacher = create_user(usertype='TR', schoolid=cls.myschool.schoolid)
        cls.myuser_other = create_user(username='user2', usertype='OT',schoolid=cls.myschool.schoolid)

        # Create user programs
        for (myuser, myschoolyear) in itertools.product([cls.myuser_teacher, cls.myuser_other], [2019, DEFAULT_SCHOOL_YEAR]):
            create_user_program(gd=cls.gd, userid=myuser.userid, schoolyear=myschoolyear, schoolid=myuser.schoolid, programname=cls.myprogram1.programname, createoptions={'drive':True}) # TO-DO: Update for multiple schoolid values

    def setUp(self):
        pass
    
    def testCreateProgram(self):

        # Check directories are created
        for myprogram in (self.myprogram1, self.myprogram2):
            gdfile = myprogram.gd.get_gd_file(gd_locator='program_base_year', schoolyear=myprogram.schoolyear, programname=myprogram.programname)
            self.assertTrue(gdfile)

    def testGetProgram(self):
        self.assertTrue(Program.objects.get(programname=self.myprogram1.programname, schoolid=self.myprogram1.schoolid, schoolyear=self.myprogram1.schoolyear))
        self.assertTrue(Program.objects.get_programs())
        self.assertTrue(Program.objects.all())

    def testUpdateProgram(self):
        
        # Save new values
        self.myprogram1.programdetails = {'google':{'calendar':{'id':'someid'}}}
        self.myprogram1.save()

        # Verify        
        self.assertEqual(Program.objects.get(programname=self.myprogram1.programname, schoolid=self.myprogram1.schoolid, schoolyear=self.myprogram1.schoolyear).calendarid, 'someid')

    def testDeleteProgram(self):

        newprogram = create_program(programname='new_program', schoolyear=2018, schoolid=self.myschool.schoolid, gd=self.gd, gc=self.gc) # Default GD
        newcalendarid = refresh(newprogram).programdetails['google']['calendar']['id']
        
        newprogram.delete(deleteoptions={'repository':True,'drive':True,'calendar':True}) # Permanently delete from GD
        
        # Verify files / objects are gone (program, drive, calendar)
        self.assertFalse(Program.objects.get(programname='new_program', schoolyear=2018, schoolid=newprogram.schoolid))
        self.assertFalse(newprogram.gd.get_gd_file(gd_locator='program_base_year', schoolyear=newprogram.schoolyear, programname=newprogram.programname, schoolid=newprogram.schoolid))
        self.assertFalse(newprogram.gc.get_calendar(calendarid=newcalendarid))

    def testCreateUserProgram(self):
        gdfile = self.myprogram1.gd.get_gd_file(gd_locator='program_uploads_user', schoolyear=self.myprogram1.schoolyear, programname=self.myprogram1.programname, userid=self.myuser_teacher.userid)
        self.assertTrue(gdfile)
        
    def testGetUserProgram(self): # TO-DO: update to handle multiple schoolid values
        
        myuserprogram = UserProgram.objects.get(
            userid=self.myuser_teacher.userid,
            schoolid=self.myuser_teacher.schoolid,
            schoolyear=DEFAULT_SCHOOL_YEAR,
            programname=self.myprogram1.programname,
            uploaddirflag=True,
        ) # teacher / year

        # Test user program and upload directory
        self.assertTrue(myuserprogram)
        self.assertTrue(self.gd.get_file(fileid=myuserprogram.uploaddirectoryid_gd))
        
        self.assertTrue(len(UserProgram.objects.get_user_programs(schoolyear=DEFAULT_SCHOOL_YEAR)), 2) # year
        self.assertTrue(len(UserProgram.objects.get_user_programs(userid=self.myuser_teacher.userid)), 2) # user
        self.assertEqual(UserProgram.objects.get_program_options(idfield='schoolyear', schoolyear=DEFAULT_SCHOOL_YEAR)[0][0], DEFAULT_SCHOOL_YEAR) # year options
        self.assertEqual(len(UserProgram.objects.get_program_options(idfield='schoolyear', schoolyear=DEFAULT_SCHOOL_YEAR)), 1) # no duplicates

    def testUpdateUserProgram(self):
        
        # Get first user program and make a change
        myuserprogram = UserProgram.objects.get_user_programs(userid=self.myuser_teacher.userid)[0]
        myuserprogram.details = to_json({'some_key':'some_value'})
        myuserprogram.save()

        # Re-retrieve object and verify
        myuserprogram = UserProgram.objects.get(userid=myuserprogram.userid, programname=myuserprogram.programname, schoolid=myuserprogram.schoolid, schoolyear=myuserprogram.schoolyear)
        self.assertEqual(myuserprogram.details['some_key'],'some_value')

    def testDeleteUserProgram(self):

        programname = 'new_program'
        myuserprogram = create_user_program(gd=self.gd, userid=self.myuser_teacher.userid, schoolyear=DEFAULT_SCHOOL_YEAR, schoolid=self.myuser_teacher.schoolid, programname=programname) # TO-DO: Update for multiple schoolid values
        
        # Check object exists before delete
        self.assertTrue(UserProgram.objects.get_user_programs(userid=self.myuser_teacher.userid, programname=programname))
        
        # Delete and verify
        UserProgram(userid=self.myuser_teacher.userid, schoolid=self.myuser_teacher.schoolid, programname=programname).delete()
        self.assertFalse(UserProgram.objects.get_user_programs(userid=self.myuser_teacher.userid, schoolid=self.myuser_teacher.schoolid, programname=programname)) # New program should be gone
        self.assertTrue(UserProgram.objects.get_user_programs(userid=self.myuser_teacher.userid)) # Other programs should still remain

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        
        UserProgram(userid=cls.myuser_teacher.userid, programname=cls.myprogram1.programname).delete()
        UserProgram(userid=cls.myuser_other.userid, programname=cls.myprogram1.programname).delete()
 
        cls.myuser_teacher.delete()
        cls.myuser_other.delete()
 
        cls.myprogram1.delete(deleteoptions={'repository':True,'drive':True,'calendar':True})
        cls.myprogram2.delete(deleteoptions={'repository':True,'drive':True,'calendar':True})

        delete_school(cls.myschool)
        
if __name__ == '__main__':
    unittest.main() # Run all tests