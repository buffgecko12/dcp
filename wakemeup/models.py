# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from UsefulFunctions.dbUtils import *

# Data model managers (interface between DB and objects)
class SchoolManager(models.Manager):
    def all(self):
        return get_data(self, 'SP_DCPGetSchool(%s)', (None))
    
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
         )
        
    def delete(self, mySchool):
        return delete_data('SP_DCPDeleteSchool', (mySchool.schoolid,))
    
class School(models.Model):
    
    schoolid = models.IntegerField(primary_key=True)
    schooldisplayname = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'school'
        
    # Item Manager instance
    objects = SchoolManager()
    
    def save(self):
        return School.objects.save(self)
    
    def delete(self):
        return School.objects.delete(self)





