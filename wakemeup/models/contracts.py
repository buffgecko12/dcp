from django.db import models
from UsefulFunctions.dbUtils import *
from django.contrib.postgres import JSONField

# Data model managers
class ContractManager(models.Manager):
    pass

class Contract(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    classid = models.IntegerField()
    contracttype = models.CharField(max_length=1)
    teacheruserid = models.IntegerField()
    contractvalidperiod = models.DateTimeField()
    guardianapprovalflag = models.BooleanField()
    revisiondeadlinets = models.DateTimeField()
    revisiondescription = models.CharField(max_length=500)
    revisionapprovalts = models.DateTimeField()
    studentleaderrequirements = models.CharField(max_length=500)
    teacherrequirements = models.CharField(max_length=500)
    studentrequirements = models.CharField(max_length=500)
    contractscanfile = models.BinaryField()
    contractapprovalts = models.DateTimeField()
    
    class Meta:
        managed = False
    
    # Objects manager
    objects = ContractManager()