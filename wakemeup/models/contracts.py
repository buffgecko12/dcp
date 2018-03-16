from django.db import models
from UsefulFunctions.dbUtils import *

# Data model managers
class ContractManager(models.Manager):
    def all(self):
        pass
    
    def get(self):
        pass
    
    def get_contract(self):
        pass
    
    def save(self):
        pass
    
    def complete(self):
        pass
    
    def delete(self):
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
    
    def save(self):
        return Contract.objects.save(self)
    
    def delete(self):
        return Contract.objects.delete(self)
    
    def complete(self):
        return Contract.objects.complete(self)