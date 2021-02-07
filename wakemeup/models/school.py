from django.db import models
from django.contrib.auth import get_user_model
from wakemeup.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.dataUtils import generate_options

DEFAULT_SCHOOL_YEAR = get_school_year()

### MODEL MANAGERS ###
class ClassManager(models.Manager):
    def all(self):
        return self.get_classes()
    
    def get(self, classid):
        return get_data_pk(self, 'SP_DCPGetClass(%s,%s,%s,%s,%s)', (classid, None, None, None, None))

    def get_classes(self, classid = None, schoolid = None, schoolyear = None, teacheruserid = None, classdisplayname = None):
        return get_data(self, 'SP_DCPGetClass(%s,%s,%s,%s,%s)', (classid, schoolid, schoolyear, teacheruserid, classdisplayname))
    
    def save(self, myClass):
        return save_data('SP_DCPUpsertClass', (
            myClass.classid,
            myClass.schoolid,
            myClass.schoolyear or DEFAULT_SCHOOL_YEAR, # If school year is not defined, use default
            myClass.classdisplayname,
            myClass.gradelevel,
            myClass.numstudentsurveys
            )
        )[0] # Return classid
    
    def delete(self, myClass):
        return delete_data('SP_DCPDeleteClass', (myClass.classid,))
    
    def get_class_options(self, schoolid = None, teacheruserid = None):
        
        return generate_options(
            items = self.get_classes(schoolid = schoolid, teacheruserid = teacheruserid), 
            idfield = "classid", 
            displayfield = "classdisplayname"
        )

class SchoolManager(models.Manager):
    def all(self):
        return self.get_schools()
    
    def get_schools(self, schoolid = None):
        return get_data(self, 'SP_DCPGetSchool(%s)', (schoolid,))
    
    def get(self, schoolid):
        return get_data_pk(self, 'SP_DCPGetSchool(%s)', (schoolid,))
    
    def save(self, mySchool):
        return save_data('SP_DCPUpsertSchool',
            (
                mySchool.schoolid,
                mySchool.schoolabbreviation,
                mySchool.schooldisplayname,
                mySchool.address,
                mySchool.city,
                mySchool.department
            )
         ) # Return schoolid + roles
        
    def delete(self, mySchool):
        return delete_data('SP_DCPDeleteSchool', (mySchool.schoolid,))

    def get_school_options(self, schoolid = None, displayfield = 'schoolabbreviation'):
        
        return generate_options(
            items = self.get_schools(schoolid=schoolid), 
            idfield = "schoolid", 
            displayfield = displayfield
        )

class SchoolCalendarManager(models.Manager):
    def all(self):
        return self.get_school_calendars()
     
    def get_school_calendars(self, calendaritemid = None, schoolid = None, schoolyear = DEFAULT_SCHOOL_YEAR, itemtype = None, round = None):
        return get_data(self, 'SP_DCPGetSchoolCalendar(%s,%s,%s,%s,%s)', (calendaritemid, schoolid, schoolyear, itemtype, round))
     
    def get(self, calendaritemid):
        return get_data_pk(self, 'SP_DCPGetSchoolCalendar(%s,%s,%s,%s,%s)', (calendaritemid, None, None, None, None))
     
    def save(self, mySchoolCalendar, calendarinfo = None):
        return save_data('SP_DCPUpsertSchoolCalendar',
            (
                mySchoolCalendar.calendaritemid,
                mySchoolCalendar.schoolid,
                mySchoolCalendar.schoolyear or DEFAULT_SCHOOL_YEAR,
                mySchoolCalendar.itemdate,
                mySchoolCalendar.itemtype,
                mySchoolCalendar.itemnotes,
                mySchoolCalendar.round,
                calendarinfo
            )
         )[0]
         
    def delete(self, mySchoolCalendar):
        return delete_data('SP_DCPDeleteSchoolCalendar', (mySchoolCalendar.calendaritemid, mySchoolCalendar.schoolid, mySchoolCalendar.schoolyear))
 
class SchoolRewardManager(models.Manager):
    def all(self):
        return self.get_school_rewards()
     
    def get_school_rewards(self, schoolid=None, rewardid=None, schoolyear=DEFAULT_SCHOOL_YEAR, sourcerewardid=None):
        return get_data(self, 'SP_DCPGetSchoolReward(%s,%s,%s,%s)', (schoolid, rewardid, schoolyear, sourcerewardid))
     
    def get(self, schoolid, rewardid):
        return get_data_pk(self, 'SP_DCPGetSchoolReward(%s,%s,%s,%s)', (schoolid, rewardid, None, None))
     
    def save(self, mySchoolReward, rewardinfo = None):
        return save_data('SP_DCPUpsertSchoolReward',
            (
                mySchoolReward.schoolid,
                mySchoolReward.rewardid,
                rewardinfo,
                mySchoolReward.schoolyear or DEFAULT_SCHOOL_YEAR,
                mySchoolReward.rewardvalue
            )
         )
         
    def delete(self, mySchoolReward):
        return delete_data('SP_DCPDeleteSchoolReward', (mySchoolReward.schoolid, mySchoolReward.rewardid, mySchoolReward.schoolyear))

class TeacherClassManager(models.Manager):
    def all(self):
        return self.get_teacher_classes()
    
    def get(self, teacheruserid, classid):
        return get_data_pk(self, 'SP_DCPGetTeacherClass(%s,%s)', (teacheruserid, classid))
    
    def get_teacher_classes(self, teacheruserid = None, classid = None):
        return get_data(self, 'SP_DCPGetTeacherClass(%s,%s)', (teacheruserid, classid,))

    def get_classes_id(self, teacheruserid = None, classid = None):
        id_list = []
        
        for myclass in self.get_teacher_classes(teacheruserid, classid):
            id_list.append(myclass.classid)
            
        return str(id_list).strip('[]')
    
    def save(self, myTeacherClass, classidlist = None):

        # Save general user info
        return save_data('SP_DCPUpsertTeacherClass', (
            myTeacherClass.teacheruserid,
            myTeacherClass.classid,
            classidlist
            )
        )[0] # Return teacheruserid
        
    def delete(self, myTeacherClass):
        return delete_data('SP_DCPDeleteTeacherClass', (myTeacherClass.teacheruserid, myTeacherClass.classid))
    
### MODELS ###
class School(MyModel):
    
    schoolid = models.IntegerField(primary_key=True, verbose_name='ID') # Using PK to avoid clashes with inherited tables
    schoolabbreviation = models.CharField(max_length=25, verbose_name='Colegio')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Nombre completo')
    address = models.CharField(max_length=100, verbose_name='Direcci' + mychr('o') + 'n')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    department = models.CharField(max_length=100, verbose_name='Departamento')

    objects = SchoolManager()

class SchoolCalendar(School):
     
    calendaritemid = models.IntegerField(primary_key=True)
    schoolyear = models.SmallIntegerField(verbose_name='School Year')
    itemdate = models.DateField(verbose_name='Fecha')
    itemtype = models.CharField(max_length=10)
    itemdescription = models.CharField(max_length=500)
    itemnotes = models.CharField(max_length=500)
    round = models.SmallIntegerField()
 
    objects = SchoolCalendarManager()
 
class SchoolReward(School):
     
    rewardid = models.IntegerField(primary_key=True) # Dummy field
    schoolyear = models.SmallIntegerField(verbose_name='School Year')
    rewardvalue = models.IntegerField(verbose_name='Valor')
 
    objects = SchoolRewardManager()
    
    def copy(self, targetyear, newrewardid=None):

        # Direct School Reward copy
        if not newrewardid:
            from wakemeup.models.program import Reward
            
            # Check if source reward has already been copied to target year
            sourcereward = Reward.objects.get_rewards(sourcerewardid=self.rewardid, schoolyear=targetyear)

            # Reward has already been copied
            if sourcereward:
                newrewardid = sourcereward[0].rewardid
            else:
                # Make a copy of the source reward
                newrewardid = getattr(Reward.objects.get(rewardid=self.rewardid).copy(targetyear=targetyear), 'rewardid')

        # Create new school reward
        if newrewardid:
            schoolreward = SchoolReward(schoolid=self.schoolid, rewardid=newrewardid, schoolyear=targetyear, rewardvalue=self.rewardvalue)
            schoolreward.save()
            return schoolreward

class Class(School):
    
    classid = models.IntegerField(primary_key=True, verbose_name='ID')
    schoolyear = models.SmallIntegerField(verbose_name='School Year')
    classdisplayname = models.CharField(max_length=100, verbose_name='Curso')
    gradelevel = models.SmallIntegerField(verbose_name='Grado')
    numstudentsurveys = models.SmallIntegerField()

    objects = ClassManager()

class Teacher(MyModel, get_user_model()):

    teacheruserid = models.IntegerField(primary_key=True,verbose_name='ID')
    
class TeacherClass(Teacher, Class):

    id = models.IntegerField(primary_key=True) # dummy field; each table must have PK specification

    objects = TeacherClassManager()