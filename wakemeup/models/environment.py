# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from lib.UsefulFunctions.dbUtils import *
from django.contrib.postgres.fields import JSONField

from django.contrib.auth import get_user_model

from lib.UsefulFunctions.stringUtils import mychr

# Data model managers (interface between DB and objects)
class FileManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetFile(%s)', (None,))
    
    def get(self, fileid):
        return get_data_pk(self, 'SP_DCPGetFile(%s)', (fileid,))
    
    def save(self, myFile):
        return save_data('SP_DCPUpsertFile',
            (
                myFile.fileid,
                myFile.filename,
                myFile.fileextension,
                myFile.filesize,
                myFile.filetype,
                myFile.filedescription,
                myFile.filedata,
                myFile.accessclass
            )
         )[0] # Return fileid
        
    def delete(self, myFile):
        return delete_data('SP_DCPDeleteFile', (myFile.fileid,))
            
# Data model managers (interface between DB and objects)
class SchoolManager(models.Manager):
    def all(self):
        return self.get_schools(schoolid = None)
    
    def get_schools(self, schoolid = None):
        return get_data(self, 'SP_DCPGetSchool(%s)', (schoolid,))
    
    def get(self, schoolid):
        return get_data_pk(self, 'SP_DCPGetSchool(%s)', (schoolid,))
    
    def save(self, mySchool):
        return save_data('SP_DCPUpsertSchool',
            (
                mySchool.schoolid,
                mySchool.schooldisplayname,
                mySchool.schoolabbreviation,
                mySchool.address,
                mySchool.city,
                mySchool.department,
                mySchool.datausepolicyfileid,
                mySchool.guardianapprovalpolicy
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
            
class ClassManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetClass(%s,%s,%s,%s)', (None,None,None,None))
    
    def get(self, classid):
        return get_data_pk(self, 'SP_DCPGetClass(%s,%s,%s,%s)', (classid,None,None,None))

    def get_classes(self, classid = None, schoolid = None, teacheruserid = None, classdisplayname = None):
        return get_data(self, 'SP_DCPGetClass(%s,%s,%s,%s)', (classid, schoolid, teacheruserid, classdisplayname))
    
    def save(self, myClass):
        return save_data('SP_DCPUpsertClass', (
            myClass.classid,
            myClass.schoolid,
            myClass.classdisplayname,
            myClass.gradelevel
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
    
class TeacherManager(models.Manager):
    def all(self):
        return self.get_teachers(teacheruserid = None)
    
    def get(self, teacheruserid):
        return get_data_pk(self, 'SP_DCPGetTeacher(%s)', (teacheruserid,))
    
    def get_teachers(self, teacheruserid):
        return get_data(self, 'SP_DCPGetTeacher(%s)', (teacheruserid,))
    
    def get_teacher_classes(self, myTeacher, classid):
        return get_data(self, 'SP_DCPGetTeacherClass (%s, %s)', (myTeacher.teacheruserid, classid,))
    
    def teacher_choices(self, teacheruserid = None):
        teachers = Teacher.objects.get_teachers(teacheruserid = teacheruserid)
        teacher_choices = [
            (str(myteacher.teacheruserid), myteacher.firstname + ' ' + myteacher.lastname) for myteacher in teachers
        ]
        
        return (teacher_choices)

    def update_budget(self, myTeacher, maxbudget):
        return save_data('SP_DCPUpsertTeacherBudget', (
            myTeacher.teacheruserid,
            maxbudget,
            )
        )
    
    def save(self, myTeacher):
        # Save teacher-specific info
        save_data('SP_DCPUpsertTeacher', (
            myTeacher.teacheruserid,
            None, # Max budget not changeable here
            myTeacher.classinfo,
            )
        )

        # Save general user info
        return save_data('SP_DCPUpsertUser', (
            myTeacher.teacheruserid,
            myTeacher.schoolid,
            '', # Username # Pass empty string to avoid NOT NULL requirement
            '', # Usertype
            myTeacher.firstname,
            myTeacher.lastname,
            myTeacher.defaultsignaturescanfile,
            myTeacher.phonenumber,
            myTeacher.emailaddress,
            '', # Password
            '', # Role
            myTeacher.profilepictureid,
            None, # Last login
            )
        )[0] # Return teacheruserid
        
    def delete(self, myTeacher):
        return get_user_model()(userid=myTeacher.teacheruserid).deactivate()

class TeacherBudgetManager(models.Manager):
    def all(self):
        return self.get_teacher_budgets(teacheruserid = None)
    
    def get(self, teacheruserid):
        return get_data_pk(self, 'SP_DCPGetTeacherBudget(%s)', (teacheruserid,))
    
    def get_teacher_budgets(self, teacheruserid):
        return get_data(self, 'SP_DCPGetTeacherBudget(%s)', (teacheruserid,))

class StudentManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetStudent(%s,%s)', (None,None))
    
    def get(self, studentuserid):
        return get_data_pk(self, 'SP_DCPGetStudent(%s,%s)', (studentuserid,None))

    def getclass(self, classid):
        return get_data(self, 'SP_DCPGetStudent(%s,%s)', (None,classid))
    
    def save(self, myStudent):
         # Save student-specific info
        save_data('SP_DCPUpsertStudent', (
            myStudent.studentuserid,
            myStudent.classid,
            )
         )

         # Save general user info
        return save_data('SP_DCPUpsertUser', (
            myStudent.studentuserid,
            myStudent.schoolid,
            '', # Username
            '', # Usertype
            myStudent.firstname,
            myStudent.lastname,
            myStudent.defaultsignaturescanfile,
            myStudent.phonenumber,
            myStudent.emailaddress,
            '', # Password
            '', # Role
            myStudent.profilepictureid,
            None, # Last login
            )
         )[0] # Return studentuserid
    
    def delete(self, myStudent):
        return get_user_model()(userid=myStudent.studentuserid).deactivate()
    
#     def student_choices(self, classid):
#         students = Student.objects.getclass(classid = classid) # Look up unassigned students
#         student_choices = [
#             (str(mystudent.studentuserid), (mystudent.firstname + ' ' + mystudent.lastname)) for mystudent in students
#         ]
#         
#         return (student_choices)
        
class School(models.Model):
    
    schoolid = models.IntegerField(primary_key=True, verbose_name='ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio')
    schoolabbreviation = models.CharField(max_length=25, verbose_name='Abreviatura')
    address = models.CharField(max_length=100, verbose_name='Direcci' + mychr('o') + 'n')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    department = models.CharField(max_length=100, verbose_name='Departamento')
    datausepolicyfileid = models.IntegerField(verbose_name='Politica de uso de datos')
    guardianapprovalpolicy = JSONField(verbose_name='Politica de aprobaci' + mychr('o') + 'n de tutor')

    class Meta:
        managed = False
        
    # School Manager instance
    objects = SchoolManager()
    
    def save(self):
        return School.objects.save(self)
    
    def delete(self):
        return School.objects.delete(self)

class File(models.Model):
    
    fileid = models.IntegerField(primary_key=True, verbose_name='ID')
    filename = models.CharField(max_length=500, verbose_name='Archivo')
    fileextension = models.CharField(max_length=50)
    filesize = models.IntegerField()
    filetype = models.CharField(max_length=100, verbose_name='Tipo')
    filedescription = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    filedata = models.BinaryField()
    accessclass = models.CharField(max_length=100)

    class Meta:
        managed = False
        
    # File Manager instance
    objects = FileManager()
    
    def save(self):
        return File.objects.save(self)
    
    def delete(self):
        return File.objects.delete(self)

class Class(models.Model):
    
    classid = models.IntegerField(primary_key=True, verbose_name='ID')
    schoolid = models.IntegerField(verbose_name='School ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio') # Derived field
    classdisplayname = models.CharField(max_length=100, verbose_name='Curso')
    gradelevel = models.IntegerField(verbose_name='Grado')

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
    schoolid = models.IntegerField(verbose_name='ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio')
    classinfo = JSONField(verbose_name='Cursos')
    firstname = models.CharField(max_length=100, verbose_name='Primer nombre')
    lastname = models.CharField(max_length=100, verbose_name='Apellido(s)')
    defaultsignaturescanfile = models.BinaryField(verbose_name='Firma')
    phonenumber = models.CharField(max_length=25, verbose_name='Tel' + mychr('e') + 'fono')
    emailaddress = models.CharField(max_length=250,verbose_name='Correo')
    reputationvalue = models.IntegerField(verbose_name='Reputaci' + mychr('o') + 'n')
    profilepictureid = models.IntegerField()
    
    objects = TeacherManager()
    
    class Meta:
        managed = False

    def save(self):
        return Teacher.objects.save(self)
    
    def update_budget(self, maxbudget):
        return Teacher.objects.update_budget(self, maxbudget)
    
    def delete(self):
        return Teacher.objects.delete(self)
    
    def get_teacher_classes(self, classid = None):
        return Teacher.objects.get_teacher_classes(self, classid)

    def get_classes_id(self, classid = None):
        id_list = []
        
        for myclass in self.get_teacher_classes(classid):
            id_list.append(myclass.classid)
            
        return str(id_list).strip('[]')

class TeacherBudget(models.Model):
    
    teacheruserid = models.IntegerField(primary_key=True,verbose_name='ID')
    maxbudget = models.IntegerField()
    budgetspent = models.IntegerField()
    availablebudget = models.IntegerField()
    
    objects = TeacherBudgetManager()
    
    class Meta:
        managed = False
    
class Student(models.Model):

    studentuserid = models.IntegerField(primary_key=True,verbose_name='ID')
    classid = models.IntegerField(verbose_name='Curso')
    schoolid = models.IntegerField(verbose_name='ID')
    schooldisplayname = models.CharField(max_length=100, verbose_name='Colegio')
    classinfo = JSONField(verbose_name='Cursos')
    firstname = models.CharField(max_length=100,verbose_name='Primer nombre')
    lastname = models.CharField(max_length=100,verbose_name='Apellido(s)')
    defaultsignaturescanfile = models.BinaryField(verbose_name='Firma')
    phonenumber = models.CharField(max_length=25,verbose_name='Tel' + mychr('e') + 'fono')
    emailaddress = models.CharField(max_length=250,verbose_name='Correo')
    reputationvalue = models.IntegerField(verbose_name='Reputaci' + mychr('o') + 'n')
    profilepictureid = models.IntegerField()

    # Object manager instance    
    objects = StudentManager()
    
    class Meta:
        managed = False

    def save(self):
        return Student.objects.save(self)
    
    def delete(self):
        return Student.objects.delete(self)