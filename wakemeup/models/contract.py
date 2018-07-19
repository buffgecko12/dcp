from django.db import models
from lib.UsefulFunctions.dbUtils import *
from django.contrib.postgres.fields import JSONField, DateTimeRangeField # uses tstzrange

# Data model managers
class ContractManager(models.Manager):
    def all(self):
        return self.get_contracts(self)
    
    def get(self, contractid):
        return get_data_pk(self, 'SP_DCPGetContract(%s,%s,%s,%s)', (contractid, None, None, None))
    
    def get_contracts(self, contractid = None, partyuserid = None, teacheruserid = None, excludedraftsflag = None):
        return get_data(self, 'SP_DCPGetContract(%s,%s,%s,%s)', (contractid, partyuserid, teacheruserid, excludedraftsflag)) # Add more fields as needed
    
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
                myContract.partyuserinfo
            )
        )[0]

    # TO-DO: Remove this (unused)
    def approve(self, myContract, partyuserid, approvaltype, signaturescanfile, approvalts, logonuserid):
        return save_data('SP_DCPApproveContract', 
            (
                myContract.contractid, 
                partyuserid, 
                approvaltype, 
                None, #preferredgoalid
                signaturescanfile, 
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
    
    def delete(self, myContract):
        return delete_data('SP_DCPDeleteContract', (myContract.contractid,))

class ContractGoalManager(models.Manager):
    def all(self):
        return self.get_contract_goals(None, None, None)
    
    def get(self, contractid, goalid = None):
        return get_data_pk(self, 'SP_DCPGetContractGoal(%s,%s,%s)', (contractid, goalid, None))
    
    def get_contract_goals(self, contractid = None, goalid = None, difficultylevel = None):
        return get_data(self, 'SP_DCPGetContractGoal(%s,%s,%s)', (contractid, goalid, difficultylevel))
    
    def save(self, myContractGoal):
        return save_data('SP_DCPUpsertContractGoal', 
            (
                myContractGoal.contractid, 
                myContractGoal.goalid, 
                myContractGoal.difficultylevel,
                myContractGoal.goaldescription,
                myContractGoal.achievedflag,
                myContractGoal.acceptedflag,
                myContractGoal.rewardinfo,
            )
        )[0]

    def accept(self, myContractGoal):
        return save_data('SP_DCPAcceptContractGoal', (
                myContractGoal.contractid,
                myContractGoal.goalid
            )
        )
        
    def delete(self, myContractGoal):
        return delete_data('SP_DCPDeleteContractGoal', (myContractGoal.contractid, myContractGoal.goalid,))

class ContractGoalRewardManager(models.Manager):
    def all(self):
        return self.get_contract_rewards(None, None, None)
    
    def get(self, contractid, goalid, rewardid):
        return get_data_pk(self, 'SP_DCPGetContractGoalReward(%s,%s,%s)', (contractid, goalid, rewardid))
    
    def get_contract_rewards(self, contractid = None, goalid= None, rewardid = None):
        return get_data(self, 'SP_DCPGetContractGoalReward(%s,%s,%s)', (contractid, goalid, rewardid))
    
    def save(self, myContractGoalReward):
        return save_data('SP_DCPUpsertContractGoalReward', 
            (
                myContractGoalReward.contractid, 
                myContractGoalReward.goalid, 
                myContractGoalReward.rewardid
            )
        )[0]
    
    def delete(self, myContractGoalReward):
        return delete_data('SP_DCPDeleteContractGoalReward', (myContractGoalReward.contractid, myContractGoalReward.goalid, myContractGoalReward.rewardid))

class ContractPartyManager(models.Manager):
    def all(self):
        return self.get_contract_parties(None, None, None)
    
    def get(self, contractid, partyuserid):
        return get_data_pk(self, 'SP_DCPGetContractParty(%s,%s,%s)', (contractid, partyuserid, None))
    
    def get_contract_parties(self, contractid = None, partyuserid = None, contractrole = None):
        return get_data(self, 'SP_DCPGetContractParty(%s,%s,%s)', (contractid, partyuserid, contractrole))
    
    def modify_contract_parties(self, contractid, partyuserinfo):
        return save_data('SP_DCPModifyContractParties', (contractid, partyuserinfo))

    def approve_contract(self, MyContractParty):
        return save_data('SP_DCPApproveContract', 
            (
                MyContractParty.contractid, 
                MyContractParty.partyuserid, 
                'C', 
                MyContractParty.preferredgoalid,
                MyContractParty.partyapprovalsignature, 
                MyContractParty.partylogonuserid
            )
        )

class ContractInfoManager(models.Manager):
    def all(self):
        return self.get_contract_info(None)
    
    def get(self, contractid):
        return get_data_pk(self, 'SP_DCPGetContractInfo(%s)', (contractid,))
    
    def get_contract_info(self, contractid = None):
        return get_data(self, 'SP_DCPGetContractInfo(%s)', (contractid,))

class RewardManager(models.Manager):
    def all(self):
        return self.get_rewards()
    
    def get(self, rewardid):
        return get_data_pk(self, 'SP_DCPGetReward(%s,%s,%s,%s)', (rewardid, None, True, None))
    
    def get_rewards(self, rewardid = None, createdbyuserid = None, activeflag = True, globalflag = True):
        return get_data(self, 'SP_DCPGetReward(%s,%s,%s,%s)', (rewardid, createdbyuserid, activeflag, globalflag))
    
    def save(self, myReward, globalflag = False):
        return save_data('SP_DCPUpsertReward', 
            (
                myReward.rewardid, 
                myReward.rewarddisplayname, 
                myReward.rewarddescription,
                myReward.rewardvalue,
                globalflag, 
                myReward.createdbyuserid,
            )
        )[0]
    
    def delete(self, myReward):
        return delete_data('SP_DCPDeactivateReward', (myReward.rewardid,))

class Contract(models.Model):
    
    contractid = models.IntegerField(primary_key=True, verbose_name="ID")
    classid = models.IntegerField()
    classdisplayname = models.CharField(max_length=100, verbose_name='Curso')
    contracttype = models.CharField(max_length=1)
    teacheruserid = models.IntegerField()
    teacherfirstname = models.CharField(max_length=100, verbose_name='Primer nombre')
    teacherlastname = models.CharField(max_length=100, verbose_name='Apellido(s)')
    contractvalidperiod = DateTimeRangeField(verbose_name='Plazo')
    guardianapprovalflag = models.BooleanField()
    revisiondeadlinets = models.DateTimeField(verbose_name='Fecha tope para revisar')
    revisiondescription = models.CharField(max_length=500)
    revisionapprovalts = models.DateTimeField()
    studentleaderrequirements = models.CharField(max_length=500)
    teacherrequirements = models.CharField(max_length=500)
    studentrequirements = models.CharField(max_length=500)
    contractscanfile = models.BinaryField()
    contractapprovalts = models.DateTimeField()
    contractstatus = models.CharField(max_length=1,verbose_name='Estatus')
    goalinfo = JSONField()
    partyuserinfo = JSONField()

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
    rewardinfo = JSONField()

    class Meta:
        managed = False

    objects = ContractGoalManager()
    
    def accept(self):
        return ContractGoal.objects.accept(self)

    def save(self):
        return ContractGoal.objects.save(self)
    
    def delete(self):
        return ContractGoal.objects.delete(self)    

class ContractGoalReward(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    goalid = models.IntegerField()
    rewardid = models.IntegerField()
    rewarddisplayname = models.CharField(max_length=100)
    rewarddescription = models.CharField(max_length=500)
    rewardvalue = models.IntegerField()

    class Meta:
        managed = False

    objects = ContractGoalRewardManager()
    
    def save(self):
        return ContractGoalReward.objects.save(self)
    
    def delete(self):
        return ContractGoalReward.objects.delete(self)    
    
class ContractParty(models.Model):

    # Get party attributes    
    contractid = models.IntegerField(primary_key=True)
    partyuserid = models.IntegerField()
    contractrole = models.CharField(max_length=2)
    firstname = models.CharField(max_length=100, verbose_name='Primer nombre')
    lastname = models.CharField(max_length=100, verbose_name='Apellido(s)')
    
    # Get approval attributes
    preferredgoalid = models.IntegerField()
    partyapprovalsignature = models.BinaryField() # signaturescanfile
    partyapprovalts = models.DateTimeField() # approvalts
    partylogonuserid = models.IntegerField() # logonuserid
    
    class Meta:
        managed = False
        
    objects = ContractPartyManager()
    
    # save/delete functions are combined into "modify_parties" object manager function    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def approve_contract(self):
        return ContractParty.objects.approve_contract(self)

class ContractInfo(models.Model):

    contractid = models.IntegerField(primary_key=True)
    teacheruserid = models.IntegerField()
    numparticipants = models.IntegerField()
    maxrewardvalue = models.IntegerField()
    
    class Meta:
        managed = False
        
    objects = ContractInfoManager()
    
class Reward(models.Model):

    # Get party attributes
    rewardid = models.IntegerField(primary_key=True)
    rewarddisplayname = models.CharField(max_length=100,verbose_name='Premio')
    rewarddescription = models.CharField()
    rewardvalue = models.IntegerField(verbose_name='Valor')
    createdbyuserid = models.IntegerField()
    
    class Meta:
        managed = False
        
    objects = RewardManager()
    
    def save(self, **kwargs):
        return Reward.objects.save(self, **kwargs)
    
    def delete(self):
        return Reward.objects.delete(self)
