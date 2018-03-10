# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from UsefulFunctions.dbUtils import *

from django.contrib.postgres.fields import JSONField

# Data model managers (interface between DB and objects)
class SchoolManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetSchool(%s)', (None,))
    
    def get(self, schoolid):
        return get_data_pk(self, 'SP_DCPGetSchool(%s)', (schoolid,))
    
    def save(self, mySchool):
        return save_data('SP_DCPUpsertSchool',
            (
                mySchool.schoolid,
                mySchool.schooldisplayname,
                mySchool.address,
                mySchool.city,
                mySchool.department
            )
         )[0] # Return schoolid
        
    def delete(self, mySchool):
        return delete_data('SP_DCPDeleteSchool', (mySchool.schoolid,))

class ClassManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetClass(%s)', (None,))
    
    def get(self, classid):
        return get_data_pk(self, 'SP_DCPGetClass(%s)', (classid,))
    
    def save(self, myClass):
        return save_data('SP_DCPUpsertClass', (
            myClass.classid,
            myClass.schoolid,
            myClass.classdisplayname
            )
        )[0] # Return classid
    
    def delete(self, myClass):
        return delete_data('SP_DCPDeleteClass', (myClass.classid,))
    
class School(models.Model):
    
    schoolid = models.IntegerField(primary_key=True)
    schooldisplayname = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    class Meta:
        managed = False
#         db_table = 'school'
        
    # School Manager instance
    objects = SchoolManager()
    
    def save(self):
        return School.objects.save(self)
    
    def delete(self):
        return School.objects.delete(self)

class Class(models.Model):
    
    classid = models.IntegerField(primary_key=True)
    schoolid = models.IntegerField()
    classdisplayname = models.CharField(max_length=100)

    # Class Manager instance    
    objects = ClassManager()

    class Meta:
        managed = False
#         db_table = 'class'
        
    def save(self):
        return Class.objects.save(self)
    
    def delete(self):
        return Class.objects.delete(self)




class StudentManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetStudent(%s)', (None,))
    
    def get(self, studentuserid):
        return get_data_pk(self, 'SP_DCPGetStudent(%s)', (studentuserid,))
    
    def save(self, myStudent):
        return save_data('SP_DCPUpsertStudent', (
            myStudent.studentuserid,
            myStudent.classid
            )
         )[0] # Return studentuserid
    
    def delete(self, myStudent):
        pass # No use-case

class Student(models.Model):

    studentuserid = models.IntegerField(primary_key=True)
    classid = models.IntegerField()
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    defaultsignaturescanfile = models.BinaryField()
    phonenumber = models.CharField(max_length=25)
    emailaddress = models.CharField(max_length=250)
    reputationvalue = models.IntegerField()
    last_login = models.DateTimeField()

    # Object manager instance    
    objects = StudentManager()
    
    class Meta:
        managed = False
#         db_table = 'user_student'

    def save(self):
        return Student.objects.save(self)
    
    def delete(self):
        return Student.objects.delete(self)
    
class TeacherManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetTeacher(%s)', (None,))
    
    def get(self, teacheruserid):
        return get_data_pk(self, 'SP_DCPGetTeacher(%s)', (teacheruserid,))
    
    def save(self, myTeacher):
        return save_data('SP_DCPUpsertTeacher', (
            myTeacher.teacheruserid,
            myTeacher.classinfo
            )
        )[0] # Return teacheruserid
        
    def delete(self, myTeacher):
        pass # No use-case
    
class Teacher(models.Model):
    teacheruserid = models.IntegerField(primary_key=True)
    classinfo = JSONField()
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    defaultsignaturescanfile = models.BinaryField()
    phonenumber = models.CharField(max_length=25)
    emailaddress = models.CharField(max_length=250)
    reputationvalue = models.IntegerField()
    last_login = models.DateTimeField()
    
    objects = TeacherManager()
    
    class Meta:
        managed = False
#         db_table = 'user_teacher'

    def save(self):
        return Teacher.objects.save(self)
    
    def delete(self):
        return Teacher.objects.delete(self)