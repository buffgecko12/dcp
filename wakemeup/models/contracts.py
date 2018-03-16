from django.db import models
from UsefulFunctions.dbUtils import *
from django.contrib.postgres.fields import JSONField, DateTimeRangeField # uses tstzrange

# Data model managers
class ContractManager(models.Manager):
    def all(self):
        return self.get_contracts(self, (None,))
    
    def get(self, contractid):
        return get_data_pk(self, 'SP_DCPGetContract(%s)', (contractid,))
    
    def get_contracts(self, contractid):
        return get_data(self, 'SP_DCPGetContract(%s)', (contractid,)) # Add more fields as needed
    
    def save(self, myContract):
        return save_data('SP_DCPUpsertContract', 
            (
                myContract.contractid, 
                myContract.classid, 
                myContract.contracttype, 
                myContract.teacheruserid, 
                myContract.contractvalidperiod, 
                myContract.guardianapprovalflag, 
                myContract.revisiondeadlinets, 
                myContract.revisiondescription, 
                myContract.studentleaderrequirements, 
                myContract.teacherrequirements, 
                myContract.studentrequirements, 
                myContract.contractscanfile, 
                myContract.goalinfo, 
                myContract.rewardinfo, 
                myContract.partyinfo
            )
        )[0]

    def complete(self):
        pass
    
    def delete(self):
        pass

class ContractGoalManager(models.Manager):
    def all(self):
        pass
    
    def get(self):
        pass
    
    def get_contract_goals(self):
        pass

class ContractRewardManager(models.Manager):
    def all(self):
        pass
    
    def get(self):
        pass
    
    def get_contract_rewards(self):
        pass

class ContractParty(models.Manager):
    def all(self):
        pass
    
    def get(self):
        pass
    
    def get_contract_parties(self):
        pass
    
class Contract(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    classid = models.IntegerField()
    contracttype = models.CharField(max_length=1)
    teacheruserid = models.IntegerField()
    contractvalidperiod = DateTimeRangeField()
    guardianapprovalflag = models.BooleanField()
    revisiondeadlinets = models.DateTimeField()
    revisiondescription = models.CharField(max_length=500)
    revisionapprovalts = models.DateTimeField()
    studentleaderrequirements = models.CharField(max_length=500)
    teacherrequirements = models.CharField(max_length=500)
    studentrequirements = models.CharField(max_length=500)
    contractscanfile = models.BinaryField()
    contractapprovalts = models.DateTimeField()
    goalinfo = JSONField() # TO-DO: Move these JSON fields to separate SP calls
    rewardinfo = JSONField()
    partyinfo = JSONField()

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