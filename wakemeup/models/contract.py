from django.db import models
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.emailUtils import send_email
from django.contrib.postgres.fields import JSONField, DateTimeRangeField # uses tstzrange

from wakemeup.models.environment import Teacher

# Data model managers
class ContractManager(models.Manager):
    def all(self):
        return self.get_contracts(self)
    
    def get(self, contractid):
        return get_data_pk(self, 'SP_DCPGetContract(%s,%s,%s,%s,%s)', (contractid, None, None, None, None))
    
    def get_contracts(self, contractid = None, partyuserid = None, teacheruserid = None, excludedraftsflag = None, excluderevisionsflag = True):
        return get_data(self, 'SP_DCPGetContract(%s,%s,%s,%s,%s)', (contractid, partyuserid, teacheruserid, excludedraftsflag, excluderevisionsflag)) # Add more fields as needed
    
    def save(self, myContract):
        return save_data('SP_DCPUpsertContract', 
            (
                myContract.contractid, 
                myContract.contractname, 
                myContract.classid, 
                myContract.contracttype, 
                myContract.teacheruserid, 
                myContract.contractvalidperiod, 
                myContract.guardianapprovalflag, 
                myContract.revisiondeadlinets, 
                myContract.studentleaderrequirements, 
                myContract.teacherrequirements, 
                myContract.studentrequirements, 
                myContract.contractscanfile, 
                myContract.goalinfo, 
                myContract.partyuserinfo
            )
        )[0]

    def revise(self, myContract, actiontype, revisiondescription, revisionrevoteflag):
        return save_data('SP_DCPReviseContract', 
            (
                myContract.contractid, 
                actiontype,
                revisiondescription,
                revisionrevoteflag
            )
        )[0]
        
    def change_status(self, myContract, contractstatus):
        return save_data('SP_DCPChangeContractStatus', 
            (
                myContract.contractid, 
                contractstatus
            )
        )
    
    def complete(self):
        pass
    
    def delete(self, myContract, sendnotifications):
        return delete_data('SP_DCPDeleteContract', (myContract.contractid, sendnotifications, ))

    def get_emails(self, myContract, emailtype, useridlist):
        emails = []

        # Get contract party e-mails
        if(emailtype == "party"):

            # Loop through contract parties
            for contractparty in myContract.partyuserinfo['currentparties']:
                if(
                    not useridlist or # all users
                    (int(contractparty['partyuserid']) in useridlist) # Only specified users
                ):
                    # Add e-mail address - individual user
                    if(not contractparty['groupuserinfo']):
                        emails.append(contractparty['emailaddress'])
                        
                    # Add e-mail addresses - group users
                    else:
                        for mygroupuser in contractparty['groupuserinfo']:
                            emails.append(mygroupuser['emailaddress'])
                
        # Get teacher e-mail
        elif(emailtype == "teacher"):
            emails.append(Teacher.objects.get(teacheruserid = myContract.teacheruserid).emailaddress)

        return emails

    def get_users(self, myContract, usertype):
        users = []

        # Loop through contract parties
        for contractparty in myContract.partyuserinfo['currentparties']:
            
            # Add e-mail address - individual user
            if(not contractparty['groupuserinfo']):
                users.append(contractparty['partyuserid'])
                
            # Add e-mail addresses - group users
            else:
                for mygroupuser in contractparty['groupuserinfo']:
                    users.append(mygroupuser['partyuserid_group'])
                
        users.append(myContract.teacheruserid)

        return users

    def send_emails(self, myContract, email_subject, email_body, useridlist):

        # Only send e-mails to specified users
        if(useridlist):
            send_email(subject=email_subject, body=email_body, to_list=myContract.get_emails(emailtype="party", useridlist=useridlist))

        # Send e-mails to all contract parties
        else:
            send_email(subject=email_subject, body=email_body, to_list=myContract.get_emails(emailtype="party"))
            send_email(subject=email_subject, body=email_body, to_list=myContract.get_emails(emailtype="teacher"))

class ContractGoalManager(models.Manager):
    def all(self):
        return self.get_contract_goals()
    
    def get(self, contractid, goalid = None):
        return get_data_pk(self, 'SP_DCPGetContractGoal(%s,%s,%s,%s)', (contractid, goalid, None, None))
    
    def get_contract_goals(self, contractid = None, goalid = None, difficultylevel = None, acceptedflag = None):
        return get_data(self, 'SP_DCPGetContractGoal(%s,%s,%s,%s)', (contractid, goalid, difficultylevel, acceptedflag))
    
    def save(self, myContractGoal):
        return save_data('SP_DCPUpsertContractGoal', 
            (
                myContractGoal.contractid, 
                myContractGoal.goalid, 
                myContractGoal.difficultylevel,
                myContractGoal.goaldescription,
                myContractGoal.acceptedflag,
                myContractGoal.rewardinfo,
                myContractGoal.maxnumrewards,
                myContractGoal.rewardselectedby
            )
        )[0]

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
                MyContractParty.partylogonuserid,
                MyContractParty.guardianapprovalinfo,
            )
        )[0]

class ContractInfoManager(models.Manager):
    def all(self):
        return self.get_contract_info(None)
    
    def get(self, contractid, allowrevisioncontractflag = None):
        return get_data_pk(self, 'SP_DCPGetContractInfo(%s,%s)', (contractid, allowrevisioncontractflag))
    
    def get_contract_info(self, contractid = None, allowrevisioncontractflag = None):
        return get_data(self, 'SP_DCPGetContractInfo(%s,%s)', (contractid, allowrevisioncontractflag))

    def get_contract_value(self, teacheruserid = None, contractid = None, numparticipants = None, allowcontractrevisionflag = False):
        return get_data(self, 'SP_DCPGetContractValue(%s,%s,%s,%s)', (teacheruserid, contractid, numparticipants, allowcontractrevisionflag, ))

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
    contractname = models.CharField(max_length=100, verbose_name="Actividad")
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
    contractapprovalts = models.DateTimeField(verbose_name='Fecha de aprobaci' + chr(243) + 'n')
    contractstatus = models.CharField(max_length=1,verbose_name='Estatus')
    goalinfo = JSONField()
    partyuserinfo = JSONField()

    class Meta:
        managed = False
    
    # Objects manager
    objects = ContractManager()
    
    def save(self):
        return Contract.objects.save(self)
    
    def revise(self, actiontype, revisiondescription = None, revisionrevoteflag = None):
        return Contract.objects.revise(self, actiontype, revisiondescription, revisionrevoteflag)
    
    def delete(self, sendnotifications = True):
        return Contract.objects.delete(self, sendnotifications)
    
    def complete(self):
        return Contract.objects.complete(self)
    
    def change_status(self, contractstatus):
        return Contract.objects.change_status(self, contractstatus)

    def get_emails(self, emailtype, useridlist = None):
        return Contract.objects.get_emails(self, emailtype, useridlist)

    def get_users(self, usertype = "all"):
        return Contract.objects.get_users(self, usertype)

    def send_emails(self, email_subject, email_body, useridlist = None):
        return Contract.objects.send_emails(self, email_subject, email_body, useridlist)

class ContractGoal(models.Model):
    
    contractid = models.IntegerField(primary_key=True)
    goalid = models.IntegerField()
    difficultylevel = models.CharField(max_length=1)
    goaldescription = models.CharField(max_length=500)
    acceptedflag = models.NullBooleanField()
    rewardinfo = JSONField()
    maxnumrewards = models.IntegerField()
    rewardselectedby = models.CharField(max_length=2)

    class Meta:
        managed = False

    objects = ContractGoalManager()
    
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
    groupinfo = JSONField()
    
    # Get approval attributes
    preferredgoalid = models.IntegerField()
    partyapprovalsignature = models.BinaryField() # signaturescanfile
    guardianapprovalinfo = JSONField()
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
    contractvalue = models.IntegerField()
    
    class Meta:
        managed = False
        
    objects = ContractInfoManager()
    
class Reward(models.Model):

    # Get party attributes
    rewardid = models.IntegerField(primary_key=True)
    rewarddisplayname = models.CharField(max_length=100,verbose_name='Premio')
    rewarddescription = models.CharField(max_length=500,verbose_name='Descripci' + chr(243) + 'n')
    rewardvalue = models.IntegerField(verbose_name='Valor')
    createdbyuserid = models.IntegerField()
    globalflag = models.BooleanField()
    
    class Meta:
        managed = False
        
    objects = RewardManager()
    
    def save(self, **kwargs):
        return Reward.objects.save(self, **kwargs)
    
    def delete(self):
        return Reward.objects.delete(self)
