# -*- coding: utf-8 -*-
import test.test_env_setup
from test.test_setup import *
from django.contrib.auth import get_user_model
from wakemeup.models.school import *
from wakemeup.models.program import *

from lib.UsefulFunctions.stringUtils import *
import json

MAX_BUDGET = 400000
PASSWORD = "adminadmin"

def create_users(userlist):
    for myuser in userlist:
        
        # Create user
        newuser = create_user(
            usertype = myuser['usertype'], 
            schoolid = myuser['schoolid'], 
            firstname = myuser['firstname'],
            lastname = myuser['lastname'],
            password = PASSWORD,
            username = normalize_field(myuser['firstname']), 
            emailaddress = normalize_field(myuser['firstname']) + '@' + normalize_field(myuser['lastname']) + '.com', # Remove on production
        )

        # Teacher info
        if(newuser.usertype == "TR"):
            
            myclassinfo = []
            myclasslist = myuser.get('classlist')
            
            # Convert class name list to classid list
            for myclass in myclasslist:
                myclassinfo.append(Class.objects.get_classes(schoolid = newuser.schoolid, classdisplayname = myclass)[0].classid)
            
            # Assign teacher classes
            myteacherclass = TeacherClass(teacheruserid = newuser.userid).save(classidlist=myclassinfo)
            
            # Set program info
            myteacherprogram = TeacherProgram(
                teacheruserid = newuser.userid, 
                schoolyear = None, # Use default
                schoolid = newuser.schoolid, 
                maxbudget = MAX_BUDGET
            )

def load_schools_classes():

    global GLV_SCHOOLID
    global ITIRR_SCHOOLID

    classes_glv = [
        (7,'702'),(7,'704'),(7,'706'),
        (10,'1002'),(10,'1006'),(10,'1007'),
        (12,'1201'),
     ]
    
    classes_rr = [
        (6,'601'),(6,'602'),(6,'603'),
        (7,'701'),(7,'702'),(7,'703'),
        (8,'801'),(8,'802'),(8,'803'),
        (9,'901'),(9,'902'),(9,'903'),
        (12,'1201'),
    ]
    
    schools = [
#         ('GLV','Guillermo Leon Valencia Colegio (sede integrado)','GLV (Integrado)', 'Calle 15A Nro 7 - 48','Duitama','Boyaca',classes_glv),
#         ('ITIRR','Instituto Técnico Industrial Rafael Reyes', 'ITIRR', 'Carrera 18 # 23-116','Duitama','Boyaca',classes_rr),
        {
            "schoolabbreviation":"GLV",
            "schooldisplayname":"Guillermo Leon Valencia Colegio (sede integrado)",
            "address":"Calle 15A Nro 7 - 48",
            "city":"Duitama",
            "department":"Boyac" + mychr('a'),
            "classes":classes_glv
        },
        {
            "schoolabbreviation":"ITIRR",
            "schooldisplayname":"Instituto Técnico Industrial Rafael Reyes",
            "address":"Carrera 18 # 23-116",
            "city":"Duitama",
            "department":"Boyac" + mychr('a'),
            "classes":classes_rr
        },
    ]
    
    for school in schools:
        myschool = School(
            schoolid = None, 
            schooldisplayname = school['schooldisplayname'], 
            schoolabbreviation = school['schoolabbreviation'], 
            address = school['address'], 
            city = school['city'], 
            department = school['department']
        )
        
        # Create school
        myschoolid = myschool.save()[0]

        if(school['schoolabbreviation'] == "GLV"):
            GLV_SCHOOLID = myschoolid
        elif(school['schoolabbreviation'] == "ITIRR"):
            ITIRR_SCHOOLID = myschoolid

        # Save classes        
        for myclass in school['classes']:
            mynewclass = Class(schoolid = myschoolid, classid = None, gradelevel = myclass[0], classdisplayname = myclass[1])
            mynewclass.save()

def load_users():
    user_list = [
        {"usertype":"SU", "schoolid":None, "firstname":"admin","lastname":"admin"},
        {"usertype":"TR", "schoolid":GLV_SCHOOLID, "firstname":"Chris","lastname":"Khosravi","classlist":["1201"]},
    ]

    create_users(user_list)

def load_rewards():
    reward_list = [
        {"rewarddisplayname":"Tiquete al cine", "rewarddescription":"Tiquete al cine.", "rewardvalue":6500, "vendor":"Innovo"},
        {"rewarddisplayname":"Hamburguesa", "rewarddescription":"Hamburguesa y papas y gaseosa.", "rewardvalue":6000,"vendor":"Cowfish"},
        {"rewarddisplayname":"B" + mychr("a") + "lon de f" + mychr("u") + "tbol", "rewarddescription": "B" + mychr("a") + "lon de f" + mychr("u") + "tbol", "rewardvalue":15000,"vendor":None}
    ]

    for reward in reward_list:
        Reward(
            rewarddisplayname = reward['rewarddisplayname'],
            rewarddescription = reward['rewarddescription'],
            rewardvalue = reward['rewardvalue'],
            vendor = reward['vendor'],
        ).save()

def load_authorization():
    
    ''' User types
    SU - Super user
    SA - Site admin
    AD - Admin (program administrator)
    TR - teacher
    ST - student
    SF - school staff
    OT - other
    '''
    
    # User roles
    myrole_public = create_role(name='Public',description='All users',publicflag=True)
    myrole_super = create_role(name='Super user',description='Full access',usertypelist=['SU'])
    myrole_admin = create_role(name='Site administrator',description='Access to administer site',usertypelist=['SA'])
    myrole_teachers = create_role(name='Teacher',description='Teachers',usertypelist=['TR'])
    myrole_staff = create_role(name='Staff',description='School staff',usertypelist=['SF'])
    myrole_program_admin = create_role(name='Program administrator',description='Program administrator (i.e. buyer, coordinator)',usertypelist=['AD'])
    myrole_program_coordinator = create_role(name='Program coordinator',description='Coordinate program at a school (usually a teacher)')
    myrole_program_purchaser = create_role(name='Program purchaser',description='Coordinate purchase and delivery of incentives')

    # Object roles
    myrole_view_program = create_role(name='view_program',description='View access on program objects',usertypelist=['TR']) # Teachers
    myrole_edit_program = create_role(name='edit_program',description='Edit access on program objects')
    myrole_delete_program = create_role(name='delete_program',description='Delete access on program objects',usertypelist=['SU','SA']) # Super user, site admin
    
    # Default business objects
    myobj_user = create_object(objectclass='BO',objectname='user')
    myobj_contract = create_object(objectclass='BO',objectname='contract')
    myobj_school = create_object(objectclass='BO',objectname='school')
    myobj_class = create_object(objectclass='BO',objectname='class')
    myobj_reward = create_object(objectclass='BO',objectname='reward')

    # Default acls - User type
    myacllist = json.dumps([
        
        # Access - Delete program
        {"roleid":myrole_delete_program.roleid,"aclinfo": 
            [
                {"objectid":myobj_school.objectid,"objectclass":myobj_school.objectclass,"accesslevel":12},     # School - delete
                {"objectid":myobj_class.objectid,"objectclass":myobj_class.objectclass,"accesslevel":12},       # Class - delete
                {"objectid":myobj_contract.objectid,"objectclass":myobj_contract.objectclass,"accesslevel":12}, # Contract - delete
                {"objectid":myobj_reward.objectid,"objectclass":myobj_reward.objectclass,"accesslevel":12},     # Reward - delete
            ],
        },
        
        # Access - View program
        {"roleid":myrole_view_program.roleid,"aclinfo": 
            [
                {"objectid":myobj_school.objectid,"objectclass":myobj_school.objectclass,"accesslevel":4},     # School - view
                {"objectid":myobj_class.objectid,"objectclass":myobj_class.objectclass,"accesslevel":4},       # Class - view
                {"objectid":myobj_contract.objectid,"objectclass":myobj_contract.objectclass,"accesslevel":4}, # Contract - view
                {"objectid":myobj_reward.objectid,"objectclass":myobj_reward.objectclass,"accesslevel":4},     # Reward - view
            ],
        },
        
        # Access - Public
        {"roleid":myrole_public.roleid,"aclinfo": 
            [
                {"objectid":myobj_user.objectid,"objectclass":myobj_user.objectclass,"accesslevel":8},          # User - edit (own user)
            ],
        },
        
        # Access - Super
        {"roleid":myrole_super.roleid,"aclinfo": 
            [
                {"objectid":myobj_user.objectid,"objectclass":myobj_user.objectclass,"accesslevel":12},         # User - delete
            ],
        },
        
        # Access - Admin
        {"roleid":myrole_admin.roleid,"aclinfo": 
            [
                {"objectid":myobj_user.objectid,"objectclass":myobj_user.objectclass,"accesslevel":10},         # User - create
            ],
        },
    ])

    # Save acls
    create_role_ACL(myrole=None,myobject=None,accesslevel=None,acllist=myacllist)

def load_all():
    
    # Clean out any existing schools
    delete_school(School(schoolid=1))
    delete_school(School(schoolid=2))

    load_schools_classes()
    load_users()
    load_rewards()
    load_authorization()
    
if (__name__ == '__main__'):
    load_all()