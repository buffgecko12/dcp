# -*- coding: utf-8 -*-
import test.test_env_setup
from test.test_setup import *
from django.contrib.auth import get_user_model
from wakemeup.models.school import *
from wakemeup.models.program import *
from wakemeup.models.environment import File

from lib.UsefulFunctions.stringUtils import *
from lib.UsefulFunctions.dataUtils import *
from lib.UsefulFunctions.googleUtils import GoogleDrive, get_gd_locator
from lib.UsefulFunctions.envUtils import check_env

''' SETUP SCRIPT
    User types
    SU - Super user
    SA - Site admin
    AD - Admin (program administrator)
    TR - teacher
    ST - student
    SF - school staff
    OT - other
'''

# Configurable parameters
DEFAULT_MAX_BUDGET = 10000
DEFAULT_PASSWORD = "somepassword"
CREATE_CALENDAR_FLAG = False

# Initial data
YEARS_LIST = [2018, 2019, 2020]

USER_LIST = [
    {"usertype":"SU", "schoolabbreviation":None, "firstname":"somename","lastname":"othername"},
    {"usertype":"TR", "schoolabbreviation":"SC", "firstname":"Joe","lastname":"Smith","classlist":["1201"],"maxbudget":DEFAULT_MAX_BUDGET},
    {"usertype":"TR", "schoolabbreviation":"SC", "firstname":"teacher_sc","lastname":"","sharedaccountflag":True},
    {"usertype":"ST", "schoolabbreviation":"SC", "firstname":"student_sc","lastname":"","sharedaccountflag":True},
]

SCHOOL_LIST = [
    {
        "schoolabbreviation":"SC",
        "schooldisplayname":"Sample Colegio",
        "address":"Calle 1 No 2-40",
        "city":"Some City",
        "department":"'Some department",
        "classes": [
            (12,'1201'),
        ]
    },
]

REWARD_LIST = [
    {
        "rewarddisplayname":"Cine (2D)", 
        "rewarddescription":"Tiquete al cine (2D).", 
        "rewardvalue":1000, 
        "rewardcategory": "ET", 
        "vendor":"Vendor A"
    },
    {
        "rewarddisplayname":"Hamburguesa con bebida", 
        "rewarddescription":"Bono para hamburguesa y bebida", 
        "rewardvalue":1000,
        "rewardcategory": "FD", 
        "vendor":"Vendor B"
    },
    {
        "rewarddisplayname":"Class Reader", 
        "rewarddescription": "", 
        "rewardvalue":2000,
        "rewardcategory": "AC", 
        "vendor": "Vendor C"
    },
    {
        "rewarddisplayname":"Diccionario", 
        "rewarddescription": "Diccionario espa" + mychr('n') + "ol-ingl" + mychr("e") + "s", 
        "rewardvalue":2500,
        "rewardcategory": "AC", 
        "vendor": "Vendor D"
    }
]

OBJECT_LIST = {
    'user':{'objectclass':'BO','objectname':'user'},
    'contract':{'objectclass':'BO','objectname':'contract'},
    'school':{'objectclass':'BO','objectname':'school'},
    'class':{'objectclass':'BO','objectname':'class'},
    'reward':{'objectclass':'BO','objectname':'reward'},
    'teacher':{'objectclass':'BO','objectname':'teacher'},
    'file':{'objectclass':'BO','objectname':'file'},
    'calendar':{'objectclass':'BO','objectname':'calendar'},
    'permissions':{'objectclass':'BO','objectname':'permissions'},
    'admintools':{'objectclass':'VW','objectname':'admintools'}
}

ROLE_LIST = {
    # User roles
    'role_public':{'roleclass':'US','name':'Public','description':'All users','publicflag':True},
    'role_super_user':{'roleclass':'US','name':'Super user','description':'Full access','usertypelist':['SU']},
    'role_site_admin':{'roleclass':'US','name':'Site Administrator','description':'Access to administer site','usertypelist':['SA']},
    'role_admin':{'roleclass':'US','name':'Site Admins (Super User and Site Administrator)','description':'Access to administer site','usertypelist':['SA','SU']},
    'role_teacher':{'roleclass':'US','name':'Teacher','description':'Teachers','usertypelist':['TR']},
    'role_staff':{'roleclass':'US','name':'Staff','description':'School staff','usertypelist':['SF']},
    'role_program_admin':{'roleclass':'PG','name':'Program Administrator','description':'Program administrator (i.e. buyer, coordinator)','usertypelist':['AD']},
    'role_program_coordinator':{'roleclass':'PG','name':'Program Coordinator','description':'Coordinate program at a school (usually a teacher)'},
    'role_program_purchaser':{'roleclass':'PG','name':'Program Purchaser','description':'Cordinate purchase and delivery of incentives'},
    
    # Object roles
    # Program
    'role_get_program':{'roleclass':'PG','name':'Program - View','description':'Read access on program objects','usertypelist':['TR']},
    'role_edit_program':{'roleclass':'PG','name':'Program - Edit','description':'Edit access on program objects'},
    'role_delete_program':{'roleclass':'PG','name':'Program - Delete','description':'Delete access on program objects','usertypelist':['SU','SA']},
    
    # Files
    'role_get_file':{'roleclass':'FL','name':'File - View','description':'Read/download access on files','publicflag':True},
    'role_create_file':{'roleclass':'FL','name':'File - Edit','description':'Create access on files','usertypelist':['TR']},
    'role_delete_file':{'roleclass':'FL','name':'File - Delete','description':'Delete access on files','usertypelist':['SU','SA']},
    
    # Calendar
    'role_get_calendar':{'roleclass':'OT','name':'Calendar - View','description':'Read access on calendar','publicflag':True},

    # Contract
    'role_get_contract':{'roleclass':'PG','name':'Contract - View','description':'Read access on contracts','usertypelist':['ST']},
    'role_create_contract':{'roleclass':'PG','name':'Contract - Create','description':'Create access on contracts','usertypelist':['TR','SA']},
    'role_delete_contract':{'roleclass':'PG','name':'Contract - Delete','description':'Delete access on contracts','usertypelist':['SU']},
    
}

ADMIN_OBJECTS = ['school','class','contract','reward','teacher']

# Default ACLs
ACL_LIST = {
    # DEFAULT PERMISSIONS
    # Program
    'role_get_program': [{"object":myobject,"accesslevel":4} for myobject in ADMIN_OBJECTS], # View program (teacher)
    'role_delete_program': [{"object":myobject,"accesslevel":12} for myobject in ADMIN_OBJECTS], # Delete program (super user, site admin)

    # File
    'role_get_file':[{'object':'file','accesslevel':4}],
    'role_create_file':[{'object':'file','accesslevel':10}],
    'role_delete_file':[{'object':'file','accesslevel':12}],

    # Calendar
    'role_get_calendar':[{'object':'calendar','accesslevel':4}],
    
    # Contract
    'role_get_contract':[{'object':'contract','accesslevel':4}],
    'role_create_contract':[{'object':'contract','accesslevel':10}],
    'role_delete_contract':[{'object':'contract','accesslevel':12}],
    
    # CUSTOM PERMISSIONS
    # Public
    'role_public': [
        {'object':'user',"accesslevel":8},
        {'object':'reward',"accesslevel":1},
    ],

    # Admins
    'role_admin':[
        {'object':'admintools','accesslevel':8}, # Execute admin tools
    ],

    # Site admin
    'role_site_admin': [{'object':'user',"accesslevel":10}], # Create user

    # Super user
    'role_super_user': [
        {'object':'user',"accesslevel":12}, # Delete user
        {'object':'permissions',"accesslevel":8} # Edit permissions
    ], # Delete user
}

INCENTIVE_PROGRAM = 'incentive'

# Initial Google Drive directory structure
GD_STRUCTURE = {
    ('Programas' + ' - ' + check_env()) :{
        'Programa de Incentivos':{
            'Subidas':{'metadata':{'gd_locator':get_gd_locator('program_uploads_base'),'programname':INCENTIVE_PROGRAM}},
            'metadata':{'gd_locator':get_gd_locator('program_base'),'programname':INCENTIVE_PROGRAM}
            },
        'metadata':{'parentid':'root','gd_locator':get_gd_locator('programs_base')} # Optional (can also exclude "parentid" or use "None")
    },
}

def create_users(userlist):
    for myuser in userlist:
        
        myschool = get_matching_item(SCHOOL_LIST,'schoolabbreviation',myuser['schoolabbreviation'])
        
        # Create user
        newuser = create_user(
            usertype = myuser['usertype'], 
            schoolid = myuser.get('schoolid') or (myschool and myschool.get('schoolid')),
            firstname = myuser['firstname'],
            lastname = myuser['lastname'],
            password = DEFAULT_PASSWORD,
            username = normalize_field(myuser['firstname']), 
            emailaddress = normalize_field(myuser['firstname']) + '@' + normalize_field(myuser['lastname']) + '.com', # TO-DO: Remove on production
            sharedaccountflag = myuser.get('sharedaccountflag')
        )

        # Teacher info
        if(newuser.usertype == "TR"):
            
            myclassinfo = []
            myclasslist = myuser.get('classlist', [])
            
            # Convert class name list to classid list
            for myclass in myclasslist:
                myclassinfo.append(Class.objects.get_classes(schoolid=newuser.schoolid, classdisplayname=myclass)[0].classid)
            
            # Assign teacher classes
            myteacherclass = TeacherClass(teacheruserid=newuser.userid).save(classidlist=myclassinfo)
            
            # Set program info
            myuserprogram = UserProgram(
                programname = INCENTIVE_PROGRAM,
                userid = newuser.userid, 
                schoolid = newuser.schoolid, 
                schoolyear = None, # Use default
                maxbudget = myuser.get('maxbudget') or DEFAULT_MAX_BUDGET
            ).save()

def setup_schools(schools):

    # Initialize counter
    counter = 0

    # Loop through school list
    for school in schools:
        
        # Create school and save id
        myschoolid = School(
            schooldisplayname = school['schooldisplayname'], 
            schoolabbreviation = school['schoolabbreviation'], 
            address = school['address'], 
            city = school['city'], 
            department = school['department']
        ).save()[0]

        # Update original school list with schoolid
        school['schoolid'] = myschoolid
        schools[counter]['schoolid'] = myschoolid

        # Save classes
        for myclass in school['classes']:
            Class(schoolid=school['schoolid'], classid=None, gradelevel=myclass[0], classdisplayname=myclass[1]).save()

        # Increment counter
        counter += 1

def setup_users(users):
    create_users(users)

def setup_rewards(rewards):
    for reward in rewards:
        Reward(**reward).save()

def setup_objects(objects):
    for objecttype, objectdata in objects.items():
        objects[objecttype] = create_object(**objectdata)

def setup_roles(roles):
    for role, roledata in roles.items():
        roles[role] = create_role(**roledata) 

def setup_role_ACLs(acllist):
    create_role_ACL(myrole=None,myobject=None,accesslevel=None,acllist=acllist)

def setup_authorization(objects, roles, acls):
    
    # Create objects, roles and ACLs
    setup_objects(objects)
    setup_roles(roles)

    # Generate ACL list (after objects / roles are updated with "id" values)
    myacllist = [
            {
                "roleid":roles[myrole].roleid,
                "aclinfo":[
                    {
                        "objectid":objects[myacl['object']].objectid,
                        "objectclass":objects[myacl['object']].objectclass,
                        "accesslevel":myacl['accesslevel']
                    } for myacl in myobjectacls
                ],
            } for myrole, myobjectacls in acls.items()
        ]
    
    # Save acls
    setup_role_ACLs(myacllist)

def setup_google_drive(gd_structure, syncfiles=True):

    gd = GoogleDrive(permissions=['write','read'])

    # Create root directory entry
    File(filename='root', filedescription='Google Drive - root directory', alternatefileid=gd.get_driveid(), filesource='GD', filetype='application/vnd.google-apps.folder', fileattributes=to_json({'gd_locator':'root'})).save()
    
    # Create directory structure
    gd.create_structure(gd_structure)

    # Sync files
    if(syncfiles):
        gd.sync()

def setup_programs():

    gc = GoogleCalendar(permissions=['write'])
    gd = GoogleDrive(permissions=['write'])

    myschoollist = [[{'schoolid':0}] + SCHOOL_LIST] # 0 is general (non-school specific)

    for myprogram in multiply_lists(myschoollist, YEARS_LIST):
        myschools = myprogram[0]
        myschoolyear = myprogram[1]

        for myschool in myschools:
            myschoolid = myschool['schoolid']
            
            # Create program and save
            myprogram = Program(
                programname=INCENTIVE_PROGRAM, 
                schoolyear=myschoolyear, 
                schoolid=myschoolid, 
                gd=gd, gc=gc, 
                createoptions={
                    'calendar': CREATE_CALENDAR_FLAG, 
                    'drive': False if myschoolid else True,
                    'defaultrole': True
                } # Create directory only for general
            )

            myprogram.save()

def setup_all():

    setup_list = [
        {'item':'Schools','function':setup_schools,'kwargs':{'schools':SCHOOL_LIST}}, # Must be done before users
        {'item':'Google Drive','function':setup_google_drive,'kwargs':{'gd_structure':GD_STRUCTURE}}, # Must be done after schools
        {'item':'Programs','function':setup_programs,'kwargs':{}},
        {'item':'Users','function':setup_users,'kwargs':{'users':USER_LIST}},
        {'item':'Rewards','function':setup_rewards,'kwargs':{'rewards':REWARD_LIST}},
        {'item':'Authorization','function':setup_authorization,'kwargs':{'objects':OBJECT_LIST,'roles':ROLE_LIST,'acls':ACL_LIST}},
    ]
    
    for setup in setup_list:
        
        print("Loading " + setup['item'] + " ...", end='')
        
        # Execute function
        setup['function'](**setup['kwargs'])
        
        print("SUCCESS")

if (__name__ == '__main__'):
    setup_all()