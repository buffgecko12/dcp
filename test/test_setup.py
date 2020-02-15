import test_env_setup

from wakemeup.models.school import *
from wakemeup.models.environment import *
from wakemeup.models.program import *
from user.models.authorization import *
from lib.UsefulFunctions.miscUtils import *
from django.contrib.auth import get_user_model
from psycopg2.extras import DateTimeTZRange
from datetime import datetime, timedelta

DEFAULT_SCHOOL_YEAR = get_school_year()

def refresh(myobject):
    objecttype = type(myobject)
    objectname = myobject.__class__.__name__.lower()
    kwargs = {}
    
    if(objectname == 'contract'):
        kwargs = {"contractid":myobject.contractid}
    if(objectname == 'contractparty'):
        kwargs = {"contractid":myobject.contractid,"teacheruserid":myobject.teacheruserid,"classid":myobject.classid}
    if(objectname == 'contractpartyreward'):
        kwargs = {"contractid":myobject.contractid,"teacheruserid":myobject.teacheruserid,"classid":myobject.classid,"rewardid":myobject.rewardid}
    if(objectname == 'file'):
        kwargs = {"fileid":myobject.fileid}
    if(objectname == 'reward'):
        kwargs = {"rewardid":myobject.rewardid}
    if(objectname == 'school'):
        kwargs = {"schoolid":myobject.schoolid}
    if(objectname == 'class'):
        kwargs = {"classid":myobject.classid}
    if(objectname == 'teacherclass'):
        kwargs = {"teacheruserid":myobject.teacheruserid,"classid":myobject.classid}
    if(objectname == 'teacherprogram'):
        kwargs = {"teacheruserid":myobject.teacheruserid,"schoolyear":myobject.schoolyear}
    if(objectname == 'role'):
        kwargs = {"roleid":myobject.roleid}
    if(objectname == 'object'):
        kwargs = {"objectid":myobject.objectid,"objectclass":objectclass}
    if(objectname == 'roleacl'):
        kwargs = {"roleid":myobject.roleid,"objectid":myobject.objectid,"objectclass":myobject.objectclass}
    if(objectname == 'myuser'):
        kwargs = {"userid":myobject.userid}
        return objecttype.objects.get_user(**kwargs) # different "get" method

    return objecttype.objects.get(**kwargs)

### SCHOOL ###
def create_school(schoolabbreviation = 'School 1', schooldisplayname = 'School 1 Full Name', address = None, city = None, department = None ):
    myschool = School(
        schoolabbreviation = schoolabbreviation,
        schooldisplayname = schooldisplayname,
        address = address,
        city = city,
        department = department
    )

    myschool.schoolid = myschool.save()
    return myschool

def create_class(schoolid, schoolyear = DEFAULT_SCHOOL_YEAR, classdisplayname = '901', gradelevel = 9, numstudentsurveys = 0):
    myclass = Class(
        schoolid = schoolid,
        schoolyear = schoolyear,
        classdisplayname = classdisplayname,
        gradelevel = gradelevel,
        numstudentsurveys = numstudentsurveys
    )

    myclass.classid = myclass.save()
    return myclass

### USER ###
def create_user(usertype='TR', firstname='Joe', lastname='Smith', userrole='U', emailaddress='test@email.com', password='password', username='user1', schoolid=None):

    # Delete user if exists
    try:
        checkuser = get_user_model().objects.get(username = username)
        checkuser.delete()
    except:
        pass

    # Create new user
    newuser = get_user_model().objects.create_user(
        password = password, 
        usertype = usertype, 
        firstname = firstname, 
        lastname = lastname,
        username = username,
        emailaddress = emailaddress,
        schoolid = schoolid,
        userrole = 'U'
    )

    return newuser

def create_teacher_class(teacheruserid, classid):
    myteacherclass = TeacherClass(teacheruserid=teacheruserid, classid=classid)
    myteacherclass.save()
    return myteacherclass

def create_file(filename='sampleimg',fileextension='jpg',filesize=5000,filetype=None,filedescription=None,filestore='FS',fileURL=None,\
                filepath=None,fileclass='General',filecategory='MS',contractid=None,schoolyear=DEFAULT_SCHOOL_YEAR,srcfilepath='test/img/sampleimg.jpg'):
    
    myfile = File(
        filename = filename,
        fileextension = fileextension,
        filesize = filesize,
        filetype = filetype,
        filedescription = filedescription,
        filestore = filestore,
        filedata = test_env_setup.readfile(srcfilepath) if filestore == 'DB' else None,
        fileURL = fileURL,
        filepath = filepath,
        fileclass = fileclass,
        filecategory = filecategory,
        contractid = contractid,
        schoolyear = schoolyear
    )

    myfile.fileid = myfile.save()
    return myfile

def create_contract(schoolyear=DEFAULT_SCHOOL_YEAR,contractname='My activity',round=1,contractvalidperiod=DateTimeTZRange(datetime(2020,1,1,0,0,0),datetime(2021,1,1,0,0,0)),\
                    proposalts=None,evaluationts=None,evidencets=None,contractstatus=None,notes=None,partyinfo=None,contractvalue=None):
        
    mycontract = Contract(
        contractid = None,
        schoolyear = schoolyear,
        contractname = contractname,
        round = round,
        contractvalidperiod = contractvalidperiod,
        proposalts = proposalts,
        evaluationts = evaluationts,
        evidencets = evidencets,
        contractstatus = contractstatus,
        notes = notes,
        partyinfo = partyinfo,
        contractvalue = contractvalue
    )
    
    mycontract.contractid = mycontract.save()
    return mycontract

def create_contract_party(contractid, teacheruserid, classid, numparticipants=None, numwinners=None):
    mycontractparty = ContractParty(
        contractid=contractid,
        teacheruserid=teacheruserid,
        classid=classid,
        numparticipants=numparticipants,
        numwinners=numwinners
    )
    
    mycontractparty.save()
    return mycontractparty

def create_contract_party_reward(contractid, teacheruserid, classid, rewardid, quantity=5, actualrewardvalue=10000, status=None):
    mycontractpartyreward = ContractPartyReward(
        contractid=contractid,
        teacheruserid=teacheruserid,
        classid=classid,
        rewardid=rewardid,
        quantity=quantity,
        actualrewardvalue=actualrewardvalue,
        status=status
    )
    
    mycontractpartyreward.save()
    return mycontractpartyreward

def create_reward(schoolyear=DEFAULT_SCHOOL_YEAR,rewarddisplayname='Some reward',rewardvalue=10000,rewarddescription='Some description',vendor='Vendor 1'):
    myreward = Reward(
        rewardid=None,
        schoolyear=schoolyear,
        rewarddisplayname=rewarddisplayname,
        rewardvalue=rewardvalue,
        rewarddescription=rewarddescription,
        vendor=vendor
    )
    
    myreward.rewardid=myreward.save()
    return myreward

def create_teacher_program(teacheruserid,schoolyear,schoolid,maxbudget=400000,teachersurveyts=None,studentsurveyurl=None,notes=None):
    myteacherprogram = TeacherProgram(
        teacheruserid=teacheruserid,
        schoolyear=schoolyear,
        schoolid=schoolid,
        maxbudget=maxbudget,
        teachersurveyts=teachersurveyts,
        studentsurveyurl=studentsurveyurl,
        notes=notes
    )
    
    myteacherprogram.save()
    return myteacherprogram

def create_role(name="New role",description="Some description",publicflag=None,schoollist=None,usertypelist=None,userlist=None):
    myrole = Role(
        roleid=None,
        name=name,
        description=description,
        publicflag=publicflag,
        schoollist=schoollist,
        usertypelist=usertypelist,
        userlist=userlist
        )
    
    myrole.roleid = myrole.save()
    return myrole

def create_object(objectclass="VW",objectname="download_file"):
    myobject = Object(
        objectid=None,
        objectclass=objectclass,
        objectname=objectname
        )
    
    myobject.objectid = myobject.save()
    return myobject

def create_roleACL(roleid,objectid,objectclass,accesslevel=4):
    myroleacl = RoleACL(
        roleid=roleid,
        objectid=objectid,
        objectclass=objectclass,
        accesslevel=accesslevel
        )

    myroleacl.save()
    return myroleacel
