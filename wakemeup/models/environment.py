# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from lib.UsefulFunctions.dbUtils import *
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

    def school_choices(self):
        schools = self.all()
        school_choices = [
            (str(myschool.schoolid), str(myschool.schooldisplayname)) for myschool in schools
        ]

        return(school_choices)
            
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
    
    def student_choices(self):
        students = Student.objects.getclass(0) # Look up unassigned students
        student_choices = [
            (str(mystudent.studentuserid), (mystudent.firstname + ' ' + mystudent.lastname)) for mystudent in students
        ]
        
        return (student_choices)
    
class TeacherManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetTeacher(%s)', (None,))
    
    def get(self, teacheruserid):
        return get_data_pk(self, 'SP_DCPGetTeacher(%s)', (teacheruserid,))
    
    def get_classes(self, myTeacher, classid):
        return get_data(self, 'SP_DCPGetTeacherClass (%s, %s)', (myTeacher.teacheruserid, classid,))
    
    def save(self, myTeacher):
        return save_data('SP_DCPUpsertTeacher', (
            myTeacher.teacheruserid,
            myTeacher.classinfo
            )
        )[0] # Return teacheruserid
        
    def delete(self, myTeacher):
        pass # No use-case

class StudentManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetStudent(%s,%s)', (None,None))
    
    def get(self, studentuserid):
        return get_data_pk(self, 'SP_DCPGetStudent(%s,%s)', (studentuserid,None))

    def getclass(self, classid):
        return get_data(self, 'SP_DCPGetStudent(%s,%s)', (None,classid))
    
    def save(self, myStudent):
        return save_data('SP_DCPUpsertStudent', (
            myStudent.studentuserid,
            myStudent.classid
            )
         )[0] # Return studentuserid
    
    def delete(self, myStudent):
        pass # No use-case
    
class School(models.Model):
    
    schoolid = models.IntegerField(primary_key=True, verbose_name='ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio')
    address = models.CharField(max_length=100, verbose_name='Direcci' + chr(243) + 'n')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    department = models.CharField(max_length=100, verbose_name='Departamento')

    class Meta:
        managed = False
        
    # School Manager instance
    objects = SchoolManager()
    
    def save(self):
        return School.objects.save(self)
    
    def delete(self):
        return School.objects.delete(self)

class Class(models.Model):
    
    classid = models.IntegerField(primary_key=True, verbose_name='ID')
    schoolid = models.IntegerField(verbose_name='School ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio') # Derived field
    classdisplayname = models.CharField(max_length=100, verbose_name='Curso')

    class Meta:
        managed = False
        
    # Class Manager instance    
    objects = ClassManager()

    def save(self):
        return Class.objects.save(self)
    
    def delete(self):
        return Class.objects.delete(self)

class Teacher(models.Model):
    
    teacheruserid = models.IntegerField(primary_key=True,verbose_name='ID')
    classinfo = JSONField() # TO-DO: Possibly remove and use other SP
    firstname = models.CharField(max_length=100, verbose_name='Primer nombre')
    lastname = models.CharField(max_length=100, verbose_name='Apellido(s)')
    defaultsignaturescanfile = models.BinaryField(verbose_name='Firma')
    phonenumber = models.CharField(max_length=25, verbose_name='Tel' + chr(233) + 'fono')
    emailaddress = models.CharField(max_length=250,verbose_name='Correo')
    reputationvalue = models.IntegerField(verbose_name='Reputaci' + chr(243) + 'n')
    
    objects = TeacherManager()
    
    class Meta:
        managed = False

    def save(self):
        return Teacher.objects.save(self)
    
    def delete(self):
        return Teacher.objects.delete(self)
    
    def get_classes(self, classid = None):
        return Teacher.objects.get_classes(self, classid)
    
class Student(models.Model):

    studentuserid = models.IntegerField(primary_key=True,verbose_name='ID')
    classid = models.IntegerField(verbose_name='Curso')
    firstname = models.CharField(max_length=100,verbose_name='Primer nombre')
    lastname = models.CharField(max_length=100,verbose_name='Apellido(s)')
    defaultsignaturescanfile = models.BinaryField(verbose_name='Firma')
    phonenumber = models.CharField(max_length=25,verbose_name='Tel' + chr(233) + 'fono')
    emailaddress = models.CharField(max_length=250,verbose_name='Correo')
    reputationvalue = models.IntegerField(verbose_name='Reputaci' + chr(243) + 'n')

    # Object manager instance    
    objects = StudentManager()
    
    class Meta:
        managed = False

    def save(self):
        return Student.objects.save(self)
    
    def delete(self):
        return Student.objects.delete(self)