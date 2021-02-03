# -*- coding: utf-8 -*-
import test.test_env_setup
from test.test_setup import *
from django.contrib.auth import get_user_model
from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import File

from lib.UsefulFunctions.stringUtils import *
from lib.UsefulFunctions.dataUtils import *
from lib.UsefulFunctions.googleUtils import GoogleDrive
from lib.UsefulFunctions.envUtils import check_env

import initialdata

def get_default_setup():
    
    # Must be done in correct order: 1) school, 2) googledrive, 3) program, 4) user, ...
    return [
        setup_config('school', schoollist=initialdata.SCHOOL_LIST),
        setup_config('googledrive', gd_structure=initialdata.GD_STRUCTURE),
        setup_config('program', schoollist=initialdata.SCHOOL_LIST, yearlist=initialdata.YEARS_LIST, createcalendarflag=initialdata.CREATE_CALENDAR_FLAG),
        setup_config('user', userlist=initialdata.USER_LIST, schoollist=initialdata.SCHOOL_LIST, defaultpassword=initialdata.DEFAULT_PASSWORD, defaultmaxbudget=initialdata.DEFAULT_MAX_BUDGET),
        setup_config('reward', rewardlist=initialdata.REWARD_LIST),
        setup_config('authorization', objectlist=initialdata.OBJECT_LIST, rolelist=initialdata.ROLE_LIST, acllist=initialdata.ACL_LIST)
    ]

def setup_config(item, **kwargs):
    setup_item = None

    if item == "school":
        setup_item = {'item':'Schools','function':setup_schools,'kwargs':kwargs}
    elif item == "googledrive":
        setup_item = {'item':'Google Drive','function':setup_google_drive,'kwargs':kwargs}
    elif item == "program":
        setup_item = {'item':'Programs','function':setup_programs,'kwargs':kwargs}
    elif item == "user":
        setup_item = {'item':'Users','function':setup_users,'kwargs':kwargs}
    elif item == "reward":
        setup_item = {'item':'Rewards','function':setup_rewards,'kwargs':kwargs}
    elif item == "authorization":
        setup_item = {'item':'Authorization','function':setup_authorization,'kwargs':kwargs}

    return setup_item

def setup_schools(schoollist):

    # Initialize counter
    counter = 0

    # Loop through school list
    for school in schoollist:
        
        # Create school and save id
        myschoolid = School(
            schooldisplayname=school['schooldisplayname'], 
            schoolabbreviation=school['schoolabbreviation'], 
            address=school['address'], 
            city=school['city'], 
            department=school['department']
        ).save()[0]

        # Update original school list with schoolid
        school['schoolid'] = myschoolid
        schoollist[counter]['schoolid'] = myschoolid

        # Save classes
        for myclass in school['classes']:
            Class(schoolid=school['schoolid'], classid=None, gradelevel=myclass[0], classdisplayname=myclass[1]).save()

        # Increment counter
        counter += 1

def setup_users(userlist, schoollist, defaultpassword, defaultmaxbudget):
    for myuser in userlist:
        myschool = get_matching_item(schoollist, 'schoolabbreviation', myuser['schoolabbreviation'])
        
        # Create user
        newuser = create_user(
            usertype=myuser['usertype'], 
            schoolid=myuser.get('schoolid') or (myschool and myschool.get('schoolid')),
            firstname=myuser['firstname'],
            lastname=myuser['lastname'],
            password=defaultpassword,
            username=normalize_field(myuser['firstname']), 
            emailaddress=normalize_field(myuser['firstname']) + '@' + normalize_field(myuser['lastname']) + '.com', # TO-DO: Remove for production
            sharedaccountflag=myuser.get('sharedaccountflag')
        )

        # Teacher info
        if newuser.usertype == "TR":
            myclassinfo = []
            myclasslist = myuser.get('classlist', [])
            
            # Convert class name list to classid list
            for myclass in myclasslist:
                myclassinfo.append(Class.objects.get_classes(schoolid=newuser.schoolid, classdisplayname=myclass)[0].classid)
            
            # Assign teacher classes
            myteacherclass = TeacherClass(teacheruserid=newuser.userid).save(classidlist=myclassinfo)
            
            # Set program info
            myuserprogram = UserProgram(
                programname=initialdata.INCENTIVE_PROGRAM,
                userid=newuser.userid, 
                schoolid=newuser.schoolid, 
                schoolyear=None, # Use default
                maxbudget=myuser.get('maxbudget') or defaultmaxbudget
            ).save()

def setup_rewards(rewardlist):
    for reward in rewardlist:
        Reward(**reward).save()

def setup_objects(objectlist):
    for objecttype, objectdata in objectlist.items():
        objectlist[objecttype] = create_object(**objectdata)

def setup_roles(rolelist):
    for role, roledata in rolelist.items():
        rolelist[role] = create_role(**roledata) 

def setup_role_ACLs(acllist):
    create_role_ACL(myrole=None, myobject=None, accesslevel=None, acllist=acllist)

def setup_authorization(objectlist, rolelist, acllist):
    
    # Create objects, roles and ACLs
    setup_objects(objectlist)
    setup_roles(rolelist)

    # Generate ACL list (after objects / roles are updated with "id" values)
    myacllist = [
            {
                "roleid":rolelist[myrole].roleid,
                "aclinfo":[
                    {
                        "objectid":objectlist[myacl['object']].objectid,
                        "objectclass":objectlist[myacl['object']].objectclass,
                        "accesslevel":myacl['accesslevel']
                    } for myacl in myobjectacls
                ],
            } for myrole, myobjectacls in acllist.items()
        ]
    
    # Save acls
    setup_role_ACLs(myacllist)

def setup_google_drive(gd_structure, syncfiles=True):
    gd = GoogleDrive(permissions=['write','read'])

    # Create root directory entry
    File(
        filename='root', 
        filedescription='Google Drive - root directory', 
        alternatefileid=gd.get_driveid(), 
        filesource='GD', 
        filetype='application/vnd.google-apps.folder', 
        fileattributes=to_json({'gd_locator':'root'})
    ).save()
    
    # Create directory structure
    gd.create_structure(gd_structure)

    # Sync files
    if syncfiles:
        gd.sync()

def setup_programs(schoollist, yearlist, createcalendarflag):
    gc = GoogleCalendar(permissions=['write'])
    gd = GoogleDrive(permissions=['write'])

    myschoollist = [[{'schoolid':0}] + schoollist] # 0 is general (non-school specific)

    for myprogram in multiply_lists(myschoollist, yearlist):
        myschools = myprogram[0]
        myschoolyear = myprogram[1]

        for myschool in myschools:
            myschoolid = myschool['schoolid']
            
            # Create program and save
            myprogram = Program(
                programname=initialdata.INCENTIVE_PROGRAM, 
                schoolyear=myschoolyear, 
                schoolid=myschoolid, 
                gd=gd, gc=gc, 
                createoptions={
                    'calendar': createcalendarflag, 
                    'drive': False if myschoolid else True,
                    'defaultrole': True
                } # Create directory only for general
            )

            myprogram.save()

def setup(setup_list):
    for setup in setup_list:
        print("Loading " + setup['item'] + " ...", end='')
        
        # Execute function
        setup['function'](**setup['kwargs'])
        
        print("SUCCESS")

def setup_all():
    setup(get_default_setup())

if (__name__ == '__main__'):
    setup_all()
