from django.db import models
from django.contrib.auth import get_user_model
from wakemeup.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import mychr

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
    
    def class_choices(self, schoolid = None, teacheruserid = None):
        classes = Class.objects.get_classes(schoolid = schoolid, teacheruserid = teacheruserid)
        class_choices = [
            (str(myclass.classid), myclass.classdisplayname) for myclass in classes
        ]
        
        return (class_choices)

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
         )[0] # Return schoolid
        
    def delete(self, mySchool):
        return delete_data('SP_DCPDeleteSchool', (mySchool.schoolid,))

    def school_choices(self, schoolid = None):
        schools = self.get_schools(schoolid=schoolid)
        school_choices = [
            (str(myschool.schoolid), str(myschool.schooldisplayname)) for myschool in schools
        ]

        return(school_choices)

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
    
    schoolid = models.IntegerField(primary_key=True, verbose_name='ID')
    schoolabbreviation = models.CharField(max_length=25, verbose_name='Abreviatura')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio')
    address = models.CharField(max_length=100, verbose_name='Direcci' + mychr('o') + 'n')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    department = models.CharField(max_length=100, verbose_name='Departamento')

    objects = SchoolManager()
    
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

    id = models.IntegerField(primary_key=True) # Each table must have PK specification
    objects = TeacherClassManager()