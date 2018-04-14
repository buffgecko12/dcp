from django.db import models
from lib.UsefulFunctions.dbUtils import *
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

    def approve(self, myContract, partyuserid, approvaltype, signaturescanfile, approvalts, logonuserid):
        return save_data('SP_DCPApproveContract', 
            (
                myContract.contractid, 
                partyuserid, 
                approvaltype, 
                signaturescanfile, 
                approvalts, 
                logonuserid
            )
        )
    
    def revise(self, myContract):
        return save_data('SP_DCPReviseContract', 
            (
                myContract.contractid, 
                myContract.revisiondescription
            )
        )

    def change_status(self, myContract, contractstatus):
        return save_data('SP_DCPChangeContractStatus', 
            (
                myContract.contractid, 
                contractstatus
            )
        )
    
    def complete(self):
        pass
    
    def delete(self):
        pass

class ContractGoalManager(models.Manager):
    def all(self):
        return self.get_contract_goals(None, None, None)
    
    def get(self, contractid, goalid):
        return get_data_pk(self, 'SP_DCPGetContractGoal(%s,%s,%s)', (contractid, goalid, None))
    
    def get_contract_goals(self, contractid = None, goalid = None, difficultylevel = None):
        return get_data(self, 'SP_DCPGetContractGoal(%s,%s,%s)', (contractid, goalid, difficultylevel))
    
    def modify_goals(self, contractid, goalinfo):
        return save_data('SP_DCPModifyContractGoals', (contractid, goalinfo))

    def accept(self, myContractGoal):
        return save_data('SP_DCPAcceptContractGoal', (
                myContractGoal.contractid,
                myContractGoal.goalid
            )
        )

class ContractRewardManager(models.Manager):
    def all(self):
        return self.get_contract_rewards(None, None, None)
    
    def get(self, contractid, rewardid):
        return get_data_pk(self, 'SP_DCPGetContractReward(%s,%s,%s)', (contractid, rewardid, None))
    
    def get_contract_rewards(self, contractid = None, rewardid = None, difficultylevel = None):
        return get_data(self, 'SP_DCPGetContractReward(%s,%s,%s)', (contractid, rewardid, difficultylevel))
    
    def modify_rewards(self, contractid, rewardinfo):
        return save_data('SP_DCPModifyContractRewards', (contractid, rewardinfo))

class ContractPartyManager(models.Manager):
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
    contractstatus = models.CharField(max_length=1)
    goalinfo = JSONField() # TO-DO: Move these JSON fields to separate SP calls
    rewardinfo = JSONField()
    partyinfo = JSONField()

    class Meta:
        managed = False
    
    # Objects manager
    objects = ContractManager()
    
    def save(self):
        return Contract.objects.save(self)
    
    def approve(self, partyuserid, approvaltype, signaturescanfile, approvalts, logonuserid):
        return Contract.objects.approve(self, partyuserid, approvaltype, signaturescanfile, approvalts, logonuserid)
    
    def revise(self):
        return Contract.objects.revise(self)
    
    def delete(self):
        return Contract.objects.delete(self)
    
    def complete(self):
        return Contract.objects.complete(self)
    
    def change_status(self, contractstatus):
        return Contract.objects.change_status(self, contractstatus)
    
class ContractGoal(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    goalid = models.IntegerField()
    difficultylevel = models.CharField(max_length=1)
    goaldescription = models.CharField(max_length=500)
    acceptedflag = models.NullBooleanField()
    achievedflag = models.NullBooleanField()

    class Meta:
        managed = False

    objects = ContractGoalManager()
    
    def accept(self):
        return ContractGoal.objects.accept(self)

    # save/delete functions are combined into "modify_goals" object manager function    
    def save(self):
        pass
    
    def delete(self):
        pass
    
class ContractReward(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    rewardid = models.IntegerField()
    difficultylevel = models.CharField(max_length=1)
    rewarddescription = models.CharField(max_length=500)

    class Meta:
        managed = False

    objects = ContractRewardManager()
    
    # save/delete functions are combined into "modify_goals" object manager function    
    def save(self):
        pass
    
    def delete(self):
        pass