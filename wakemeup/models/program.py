import copy

from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField, ArrayField

from wakemeup.models.school import *
from wakemeup.models.base import MyModel, Object
from wakemeup.models.environment import File
from user.models.authorization import Role, RoleACL

from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.emailUtils import send_email
from lib.UsefulFunctions.googleUtils import GoogleDrive, GoogleCalendar, get_gd_locator
from lib.UsefulFunctions.dataUtils import generate_options, to_json

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
        return get_data_pk(self, 'SP_DCPGetReward(%s,%s,%s)', (rewardid, None, None))
    
    def get_rewards(self, rewardid=None, schoolyear=DEFAULT_SCHOOL_YEAR, sourcerewardid=None):
        return get_data(self, 'SP_DCPGetReward(%s,%s,%s)', (rewardid, schoolyear, sourcerewardid))
    
    def save(self, myReward):
        return save_data('SP_DCPUpsertReward', 
            (
                myReward.rewardid, 
                myReward.schoolyear or DEFAULT_SCHOOL_YEAR,
                myReward.rewarddisplayname, 
                myReward.rewarddescription,
                myReward.rewardvalue,
                myReward.rewardcategory,
                myReward.vendor,
                myReward.sourcerewardid
            )
        )[0]
    
    def delete(self, myReward):
        return delete_data('SP_DCPDeleteReward', (myReward.rewardid,))

class ProgramManager(models.Manager):

    def all(self):
        return self.get_programs()
    
    def get(self, programname, schoolid, schoolyear):
        return get_data_pk(self, 'SP_DCPGetProgram(%s,%s,%s,%s,%s)', (programname, schoolid, schoolyear, None, None))

    def get_programs(self, programname=None, schoolid=None, schoolyear=DEFAULT_SCHOOL_YEAR, programdetails=None, excludegeneralflag=True):
        return get_data(self, 'SP_DCPGetProgram(%s,%s,%s,%s,%s)', (programname, schoolid, schoolyear, programdetails, excludegeneralflag))

    def save(self, myProgram):

        # Save data
        return save_data('SP_DCPUpsertProgram', (
            myProgram.programname,
            myProgram.schoolid,
            myProgram.schoolyear,
            to_json(myProgram.programdetails)
            )
        )

    def delete(self, myProgram, deleteoptions, *args, **kwargs):
        
        # Delete Calendar
        if(deleteoptions.get('calendar')):
            if not myProgram.programdetails:
                myprogram = Program.objects.get(programname=myProgram.programname, schoolid=myProgram.schoolid, schoolyear=myProgram.schoolyear)
            else:
                myprogram = myProgram

            try:
                myProgram.gc.delete_calendar(
                    calendarid=myprogram.programdetails['google']['calendar']['id'],
                    baseflag=True
                )
            except:
                print("API Error: Could not delete calendar")

        mygdfile = File.objects.lookup_fileid_gd(gd_locator=myProgram.gd_locator, schoolid=myProgram.schoolid, schoolyear=myProgram.schoolyear, programname=myProgram.programname)

        # Delete files
        if mygdfile:
            myProgram.gd.delete_file(
                fileid = mygdfile,
                deleteoptions=deleteoptions
            )

        # Delete program
        return delete_data('SP_DCPDeleteProgram', (myProgram.programname, myProgram.schoolid, myProgram.schoolyear))

    def create_drive(self, myProgram, *args, **kwargs):
        
        programinfo = {'schoolyear':myProgram.schoolyear,'programname':myProgram.programname}
        
        # Define directory structure
        gd_structure = {
            str(myProgram.schoolyear):{
                # Update default ACLs when creating new Program()
                'Archivos':{
                    'Contratos':{'metadata':{'gd_locator':get_gd_locator('program_files_contracts'), **programinfo}},
                    'Documentos':{'metadata':{'gd_locator':get_gd_locator('program_files_documents'), **programinfo}},
                    'Videos':{'metadata':{'gd_locator':get_gd_locator('program_files_videos'), **programinfo}},
                    'Entrevistas':{'metadata':{'gd_locator':get_gd_locator('program_files_interviews'), **programinfo}},
                    'metadata':{'gd_locator':get_gd_locator('program_files_base'), **programinfo},
                },
                'Subidas':{'metadata':{'gd_locator':get_gd_locator('program_uploads_base'), **programinfo}},
                'metadata':{
                    'parentid':File.objects.lookup_fileid_gd(gd_locator=get_gd_locator('program_base'),programname=myProgram.programname),
                    'filedescription':'Google Drive - ' + myProgram.programname + ' base directory (' + str(myProgram.schoolyear) + ')',
                    'gd_locator':myProgram.gd_locator,
                    'schoolid':myProgram.schoolid,
                    'schoolyear':myProgram.schoolyear,
                    'programname':myProgram.programname
                }
            }
        }
        
        # Build structure
        return myProgram.gd.create_structure(gd_structure)

    def create_calendar(self, myProgram, publicflag=False, *args, **kwargs):

        myschool = School.objects.get(schoolid=myProgram.schoolid)

        # schoolyear, schoolid, programname
        calendarname = "{0}{1}{2}".format(
            str(myProgram.schoolyear) + ' - ' if myProgram.schoolyear else '',
            myProgram.programname,
            ' (' + myschool.schoolabbreviation + ')' if (myschool.schoolabbreviation and myschool.schoolid) else ''
        )

        return myProgram.gc.create_calendar(title=calendarname, description='', publicflag=publicflag)

    def get_program_options(self, idfield, displayfield=None, userflag=False, **kwargs):
        return generate_options(
            items=self.get_programs(**kwargs) if not userflag else UserProgram.objects.get_user_programs(**kwargs),
            idfield=idfield,
            displayfield=displayfield or idfield,
        )

    def get_year_options(self, startyear=2000, endyear=2050, startoffset=0, endoffset=0, programrangeflag=False):

        # Use existing program years for range
        if programrangeflag:
            programs = Program.objects.get_programs(schoolyear=None)

            if programs:
                startyear = min(myprogram.schoolyear for myprogram in programs)
                endyear = max(myprogram.schoolyear for myprogram in programs)
 
        # Set new range (with offset)
        startyear = startyear - startoffset
        endyear = endyear + endoffset

        yearlist = []

        for programyear in list(range(startyear, endyear)):
            year = Object()
            year.year = programyear
            yearlist.append(year)

        return generate_options(
            items=yearlist,
            idfield='year',
            displayfield='year'
        )

class UserProgramManager(models.Manager):
    def all(self):
        return self.get_user_programs()
    
    def get(self, userid, programname, schoolid, schoolyear, uploaddirflag=False, gd=None):
        
        myuserprogram = get_data_pk(self, 'SP_DCPGetUserProgram(%s,%s,%s,%s)', (userid, programname, schoolid, schoolyear))
    
        # Create upload directory if user program exists and no uploaddirectory exists
        if(uploaddirflag and not getattr(myuserprogram,'uploaddirectoryid',True)):
            myuserprogram.gd = myuserprogram.gd or GoogleDrive(permissions=['write'])
            myuserprogram.uploaddirectoryid_gd = self.create_drive(myuserprogram,'upload')['gd_file']['id']
        
        return myuserprogram
    
    def get_user_programs(self, userid=None, programname=None, schoolid=None, schoolyear=DEFAULT_SCHOOL_YEAR):
        return get_data(self, 'SP_DCPGetUserProgram(%s,%s,%s,%s)', (userid, programname, schoolid, schoolyear))
        
    def save(self, myUserProgram):

        # Check if user program exists
        existingprogram = UserProgram.objects.get(
            userid=myUserProgram.userid, 
            programname=myUserProgram.programname, 
            schoolid=myUserProgram.schoolid, 
            schoolyear=myUserProgram.schoolyear
            )
        
        # If new user program, add user to default roles: program year - school, program year - general (0)
        if not existingprogram:            
            for myschool in (0, myUserProgram.schoolid):
                program = Program.objects.get(programname=myUserProgram.programname, schoolid=myschool, schoolyear=myUserProgram.schoolyear)
    
                # Add user to program's default role (if exists)
                if program:
                    Role(roleid=program.defaultroleid).modify_role_item(userid=myUserProgram.userid)

        myuserprogram = save_data('SP_DCPUpsertUserProgram', (
            myUserProgram.userid,
            myUserProgram.programname,
            myUserProgram.schoolid,
            myUserProgram.schoolyear or DEFAULT_SCHOOL_YEAR,
            myUserProgram.maxbudget,
            None if myUserProgram.uploaddirectoryid == '' else myUserProgram.uploaddirectoryid, # Handle case of empty string
            myUserProgram.details,
            )
        )

        return myuserprogram
        
    def delete(self, myUserProgram):
        return delete_data('SP_DCPDeleteUserProgram', (myUserProgram.userid, myUserProgram.programname, myUserProgram.schoolid, myUserProgram.schoolyear))

    def create_drive(self, myUserProgram, directorytype):

        gd = myUserProgram.gd
        
        # Check directory doesn't already exist in GD
        if directorytype == 'upload':
            mydir = gd.get_gd_file(gd_locator=get_gd_locator('program_uploads_user'), programname=myUserProgram.programname, userid=myUserProgram.userid, schoolyear=myUserProgram.schoolyear)
        
        if not mydir:

            # Get user info
            myuser = get_user_model().objects.get_user(userid=myUserProgram.userid)
            dirname = (myuser.schoolabbreviation + ' - ' if myuser.schoolid else '') + myuser.userdisplayname

            # Define directory structure
            gd_structure = {
                dirname:{
                    'metadata':{
                        'parentid':File.objects.lookup_fileid_gd(gd_locator=get_gd_locator('program_uploads_base'),schoolyear=myUserProgram.schoolyear, programname=myUserProgram.programname),
                        'filedescription':'Google Drive - User Upload directory (' + str(myUserProgram.programname) + ' - ' + str(myUserProgram.schoolyear) + ')',
                        'gd_locator':get_gd_locator('program_uploads_user'),
                        'schoolyear':myUserProgram.schoolyear,
                        'programname':myUserProgram.programname,
                        'userid':myUserProgram.userid
                    }
                }
            }
            
            # Build structure
            newfile = gd.create_structure(gd_structure)
        
            # Update program with file id
            myUserProgram.uploaddirectoryid = newfile['fileid']
            myUserProgram.save()
            
            # Return newly created GoogleId
            return newfile
        
        else:
            # Handle case of file in GD, but not in repository
            pass

class Reward(MyModel):

    rewardid = models.IntegerField(primary_key=True)
    schoolyear = models.SmallIntegerField()
    rewarddisplayname = models.CharField(max_length=100,verbose_name='Incentivo')
    rewarddescription = models.CharField(max_length=500,verbose_name='Descripci' + mychr('o') + 'n')
    rewardvalue = models.IntegerField(verbose_name='Valor')
    rewardcategory = models.CharField(max_length=10, verbose_name='Categor' + mychr('i') + 'a')
    rewardcategorydisplayname = models.CharField(max_length=100, verbose_name='Categor' + mychr('i') + 'a')
    vendor = models.CharField(max_length=100,verbose_name='Vendedor')
    sourcerewardid = models.IntegerField() # (internal) may not be needed
    rewardchildren = ArrayField(models.IntegerField())
    
    objects = RewardManager()

    def copy(self, targetyear, copyoptions={'copyschools':False}):

        # Make sure reward has not already been copied to target yet
        if not Reward.objects.get_rewards(schoolyear=targetyear, sourcerewardid=self.rewardid):

            # Copy original reward and update values
            newreward = copy.deepcopy(self)
            newreward.rewardid = None # Clear existing rewardid
            newreward.sourcerewardid = self.rewardid # Store source rewardid
            newreward.schoolyear = targetyear # Set to new year
    
            # Save new reward
            newreward.rewardid = newreward.save()
            
            if copyoptions.get('copyschools'):
                
                # Get all school rewards associated with this reward / school year
                schoolrewards = SchoolReward.objects.get_school_rewards(rewardid=self.rewardid, schoolyear=self.schoolyear)
                
                # Copy school rewards
                for myschoolreward in schoolrewards:
                    myschoolreward.copy(targetyear=targetyear, newrewardid=newreward.rewardid)
            
            return newreward
        
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
    partyinfo = models.JSONField()
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

class Program(MyModel):

    schoolyear = models.SmallIntegerField(primary_key=True,verbose_name='A' + mychr('n') + 'o escolar')
    schoolid = models.IntegerField()
    programname = models.CharField(max_length=50)
    programdetails = models.JSONField()
    calendarid = models.CharField(max_length=250)
    gd_locator = get_gd_locator('program_base_year')
    
    def __init__(self, *args, **kwargs):
        
        # Extract extra parameters (if any)
        createoptions = kwargs.pop('createoptions', None)
        self.gd = kwargs.pop('gd', None)
        self.gc = kwargs.pop('gc', None)
        
        # Extract "gd" if defined
        if(self.gd == "default"):
            self.gd = GoogleDrive(permissions=['write']) # Use GD if provided, otherwise get default
            
        # Extract "gc" if defined
        if(self.gc == "default"):
            self.gc = GoogleCalendar(permissions=['write']) # Use GC if provided, otherwise get default
            
        super(Program, self).__init__(*args, **kwargs)
        
        # Initialize parameters
        self.programdetails = self.programdetails or {}
        self.schoolid = self.schoolid or kwargs.get('schoolid') or 0 # Default to 0 (program-level) if not specified
        
        # Create google directory
        if(createoptions):
            self.result = {}
            
            if(createoptions.get('drive')):
                self.result['drive'] = self.create_drive()
                
            if(createoptions.get('calendar')):
                mycalendar = self.create_calendar(publicflag=True)

                # Store / return calendar info                
                self.calendarid = mycalendar
                self.programdetails['google'] = {'calendar':{'id':mycalendar['id']}} # TO-DO: Watch out here, in case overwriting provided programdetails
                
            if(createoptions.get('defaultrole')):
                schoolabbreviation = School.objects.get(schoolid=self.schoolid).schoolabbreviation

                programinfo = {'schoolyear':self.schoolyear,'programname':self.programname}
                
                # Base directories
                basedirs = [
                    File.objects.lookup_fileid(gd_locator=get_gd_locator('programs_base')),
                    File.objects.lookup_fileid(gd_locator=get_gd_locator('program_base'), programname=self.programname)
                ]
                
                # Program directories
                programdirs = [
                    File.objects.lookup_fileid(gd_locator=get_gd_locator(mydir), **programinfo) for mydir in \
                    ('program_base_year', 'program_files_base', 'program_files_contracts', 'program_files_videos', 'program_files_interviews' ,'program_files_documents')
                ]

                defaultdirs = basedirs + programdirs

                mydefaultroleid = Role(roleclass='PG', name=('Programa ({0}) - {1}' + (' - {2}' if self.schoolid else '')).format(self.programname, self.schoolyear, schoolabbreviation)).save()
                
                # Assign Default ACLs
                acllist = [
                    {"roleid":mydefaultroleid, "aclinfo":
                        [
                            {"objectid":myfileid, "objectclass":"FL", "accesslevel":4} if myfileid else () for myfileid in list(filter(None, defaultdirs)) # Read permission on directories
                        ]
                    },
                ]
                
                RoleACL().save(acllist)
                
                self.defaultroleid = mydefaultroleid
                self.programdetails['defaultroleid'] = mydefaultroleid

    objects = ProgramManager()

    def create_drive(self, *args, **kwargs):
        return Program.objects.create_drive(self, *args, **kwargs)
    
    def create_calendar(self, *args, **kwargs):
        return Program.objects.create_calendar(self, *args, **kwargs)
    
    def delete(self, deleteoptions={'repository':True, 'drive':False, 'calendar':False}, *args, **kwargs):
        return Program.objects.delete(self, deleteoptions, *args, **kwargs)

    def copy(self, targetyear, copyoptions={'copyusersflag':True}, createoptions=None, gd='default', gc='default'):
        programparams = {'programname':self.programname, 'schoolid':self.schoolid}

        # Check if new program already exists
        existingprogram = Program.objects.get(**programparams, schoolyear=targetyear)

        # Don't overwrite if program already exists
        if existingprogram:
            return existingprogram
        else:
            
            # Copy school program
            createoptions_prog = copy.deepcopy(createoptions)
            createoptions_prog.update({'drive':False})
            
            newprogram = Program(**programparams, schoolyear=targetyear, createoptions=createoptions_prog, gd=gd, gc=gc)
            newprogram.save()
            
            # Copy base program (non-school specific); schoolid = 0
            if not Program.objects.get(programname=self.programname, schoolid=0, schoolyear=targetyear):
                baseprogram = Program(programname=self.programname, schoolid=0, schoolyear=targetyear, createoptions=createoptions, gd=gd, gc=gc)
                baseprogram.save()
    
            # Copy user program
            if copyoptions.get('copyusersflag') != False:
                
                # Get user id list
                useridlist = copyoptions.get('useridlist') or []
    
                # Loop through current program's users
                for myuserprogram in UserProgram.objects.get_user_programs(**programparams, schoolyear=self.schoolyear):
                    if myuserprogram.userid in useridlist or not useridlist:
                        
                        # Copy user program
                        myuserprogram.copy(targetyear=targetyear)
    
            return newprogram

class UserProgram(Program):

    userid = models.IntegerField()
    maxbudget = models.IntegerField(primary_key=True,verbose_name='Prespuesto m' + mychr('a') + 'ximo')
    uploaddirectoryid = models.IntegerField()
    details = models.JSONField()
    
    # Derived fields
    budgetspent = models.IntegerField(verbose_name='Gastos')
    availablebudget = models.IntegerField(verbose_name='Saldo')

    def __init__(self,*args,**kwargs):

        super(UserProgram, self).__init__(*args,**kwargs)
         
        # Clear inherited value
        self.gd_locator = None

    objects = UserProgramManager()

    def create_drive(self, directorytype='upload'):
        return UserProgram.objects.create_drive(self, directorytype)
    
    def delete(self, *args, **kwargs):
        return UserProgram.objects.delete(self, *args, **kwargs)
    
    def copy(self, targetyear, createprogramflag=False):
        programparams = {'programname':self.programname, 'schoolid':self.schoolid, 'schoolyear':targetyear}
        
        # Create program (if doesn't exist)
        if not Program.objects.get(**programparams) and createprogramflag:
            Program(**programparams).save()
        
        # Save new user program
        return UserProgram(
            **programparams, 
            userid=self.userid,
            maxbudget=self.maxbudget
        ).save()
    