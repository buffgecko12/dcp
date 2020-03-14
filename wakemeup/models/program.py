from django.db import models
from wakemeup.models.base import MyModel
from wakemeup.models.school import *
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.emailUtils import send_email
from django.contrib.postgres.fields import JSONField, DateTimeRangeField

DEFAULT_SCHOOL_YEAR = get_school_year()

# Data model managers
class ContractManager(models.Manager):
    def all(self):
        return self.get_contracts(self)
    
    def get(self, contractid):
        return get_data_pk(self, 'SP_DCPGetContract(%s,%s,%s)', (contractid, None, None))
    
    def get_contracts(self, contractid = None, teacheruserid = None, schoolyear = None):
        return get_data(self, 'SP_DCPGetContract(%s,%s,%s)', (contractid, teacheruserid, schoolyear))
    
    def save(self, myContract):
        return save_data('SP_DCPUpsertContract', 
            (
                myContract.contractid, 
                myContract.schoolyear or DEFAULT_SCHOOL_YEAR, # If school year is not defined, use default
                myContract.contractname, 
                myContract.round,
                myContract.contractvalidperiod, 
                myContract.proposalts,
                myContract.evaluationts,
                myContract.evidencets,
                myContract.contractstatus,
                myContract.notes,
                myContract.partyinfo
            )
        )[0]
        
    def delete(self, myContract):
        return delete_data('SP_DCPDeleteContract', (myContract.contractid, ))

    def get_emails(self, myContract):
        pass
    
    def send_emails(self, myContract, email_subject, email_body):
        pass
#         send_email(subject=email_subject, body=email_body, to_list=myContract.get_emails())

class ContractPartyRewardManager(models.Manager):
    def all(self):
        return self.get_contract_party_rewards(None, None, None, None)
    
    def get(self, contractid, teacheruserid, classid, rewardid):
        return get_data_pk(self, 'SP_DCPGetContractPartyReward(%s,%s,%s,%s)', (contractid, teacheruserid, classid, rewardid))
    
    def get_contract_party_rewards(self, contractid = None, teacheruserid = None, classid = None, rewardid = None):
        return get_data(self, 'SP_DCPGetContractPartyReward(%s,%s,%s,%s)', (contractid, teacheruserid, classid, rewardid))

    def save(self, myContractPartyReward):
        return save_data('SP_DCPUpsertContractPartyReward', 
            (
                myContractPartyReward.contractid, 
                myContractPartyReward.teacheruserid, 
                myContractPartyReward.classid, 
                myContractPartyReward.rewardid,
                myContractPartyReward.quantity,
                myContractPartyReward.actualrewardvalue,
                myContractPartyReward.status
            )
        )[0]
    
    def delete(self, myContractPartyReward):
        return delete_data('SP_DCPDeleteContractPartyReward', (myContractPartyReward.contractid, myContractPartyReward.teacheruserid, myContractPartyReward.classid, myContractPartyReward.rewardid))

class ContractPartyManager(models.Manager):
    def all(self):
        return self.get_contract_parties(None, None, None)
    
    def get(self, contractid, teacheruserid, classid):
        return get_data_pk(self, 'SP_DCPGetContractParty(%s,%s,%s)', (contractid, teacheruserid, classid))
    
    def get_contract_parties(self, contractid = None, teacheruserid = None, classid = None):
        return get_data(self, 'SP_DCPGetContractParty(%s,%s,%s)', (contractid, teacheruserid, classid))
    
    def save(self, myContractParty):
        return save_data('SP_DCPUpsertContractParty',
             (
                 myContractParty.contractid,
                 myContractParty.teacheruserid,
                 myContractParty.classid,
                 myContractParty.numparticipants,
                 myContractParty.numwinners,
                 getattr(myContractParty, 'partyinfo', None) # handle case if not provided
             )
        )[0]
    
    def delete(self, myContractParty):
        return delete_data('SP_DCPDeleteContractParty', (myContractParty.contractid, myContractParty.teacheruserid, myContractParty.classid))
    
class RewardManager(models.Manager):
    def all(self):
        return self.get_rewards()
    
    def get(self, rewardid):
        return get_data_pk(self, 'SP_DCPGetReward(%s,%s)', (rewardid,None))
    
    def get_rewards(self, rewardid = None, schoolyear = None):
        return get_data(self, 'SP_DCPGetReward(%s,%s)', (rewardid, schoolyear))
    
    def save(self, myReward):
        return save_data('SP_DCPUpsertReward', 
            (
                myReward.rewardid, 
                myReward.schoolyear or DEFAULT_SCHOOL_YEAR,
                myReward.rewarddisplayname, 
                myReward.rewarddescription,
                myReward.rewardvalue,
                myReward.rewardcategory,
                myReward.vendor
            )
        )[0]
    
    def delete(self, myReward):
        return delete_data('SP_DCPDeleteReward', (myReward.rewardid,))

class TeacherProgramManager(models.Manager):
    def all(self):
        return self.get_teacher_programs()
    
    def get(self, teacheruserid, schoolyear):
        return get_data_pk(self, 'SP_DCPGetTeacherProgram(%s,%s)', (teacheruserid, schoolyear))
    
    def get_teacher_programs(self, teacheruserid = None, schoolyear = DEFAULT_SCHOOL_YEAR):
        return get_data(self, 'SP_DCPGetTeacherProgram(%s,%s)', (teacheruserid, schoolyear))
        
    def save(self, myTeacherProgram):
        return save_data('SP_DCPUpsertTeacherProgram', (
            myTeacherProgram.teacheruserid,
            myTeacherProgram.schoolyear or DEFAULT_SCHOOL_YEAR,
            myTeacherProgram.schoolid,
            myTeacherProgram.maxbudget,
            myTeacherProgram.teachersurveyts,
            myTeacherProgram.studentsurveyurl,
            myTeacherProgram.notes,
            )
        )
        
    def delete(self, myTeacherProgram):
        return delete_data('SP_DCPDeleteTeacherProgram', (myTeacherProgram.teacheruserid, myTeacherProgram.schoolyear))

class Reward(MyModel):

    rewardid = models.IntegerField(primary_key=True)
    schoolyear = models.SmallIntegerField()
    rewarddisplayname = models.CharField(max_length=100,verbose_name='Premio')
    rewarddescription = models.CharField(max_length=500,verbose_name='Descripci' + mychr('o') + 'n')
    rewardvalue = models.IntegerField(verbose_name='Valor')
    rewardcategory = models.CharField(max_length=10, verbose_name='Categor' + mychr('i') + 'a')
    rewardcategorydisplayname = models.CharField(max_length=100, verbose_name='Categor' + mychr('i') + 'a')
    vendor = models.CharField(max_length=100,verbose_name='Vendedor')
    
    objects = RewardManager()
    
class Contract(MyModel):

    contractid = models.IntegerField(primary_key=True, verbose_name="ID")
    schoolyear = models.SmallIntegerField()
    contractname = models.CharField(max_length=100, verbose_name="Actividad")
    round = models.SmallIntegerField(verbose_name="Ronda")
    contractvalidperiod = DateTimeRangeField(verbose_name='Plazo')
    proposalts = models.DateTimeField(verbose_name='Propuesta')
    evaluationts = models.DateTimeField(verbose_name='Evaluaci' + mychr('o') + 'n')
    evidencets = models.DateTimeField(verbose_name='Evidencias')
    contractstatus = models.CharField(max_length=1,verbose_name='Estado')
    notes = models.CharField(max_length=500,verbose_name="Notas")
    partyinfo = JSONField()
    contractvalue = models.IntegerField(verbose_name="Valor")

    # Objects manager
    objects = ContractManager()
    
    def get_emails(self):
        return Contract.objects.get_emails(self)

    def send_emails(self, email_subject, email_body):
        return Contract.objects.send_emails(self, email_subject, email_body)

class ContractParty(Contract, TeacherClass):

    numparticipants = models.SmallIntegerField(primary_key=True) # Include PK otherwise it will interfere with derived classes
    numwinners = models.SmallIntegerField()
    
    objects = ContractPartyManager()
    
class ContractPartyReward(ContractParty, Reward):
    
    quantity = models.SmallIntegerField(primary_key=True)
    actualrewardvalue = models.IntegerField()
    status = models.CharField(max_length=1)

    objects = ContractPartyRewardManager()

class TeacherProgram(Teacher):

    schoolyear = models.SmallIntegerField(primary_key=True,verbose_name='A' + mychr('n') + 'o escolar')
    maxbudget = models.IntegerField(verbose_name='Prespuesto m' + mychr('a') + 'ximo')
    budgetspent = models.IntegerField(verbose_name='Gastos')
    availablebudget = models.IntegerField(verbose_name='Saldo')
    teachersurveyts = models.DateTimeField(verbose_name='Encuesta de docente')
    studentsurveyurl = models.URLField(max_length=500)
    notes = models.CharField(max_length=500,verbose_name='Notas')
    
    objects = TeacherProgramManager()