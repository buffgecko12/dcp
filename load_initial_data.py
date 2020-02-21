# -*- coding: utf-8 -*-
import test.test_env_setup
from test.test_setup import create_user, delete_school
from django.contrib.auth import get_user_model
from wakemeup.models.school import *
from wakemeup.models.program import *

from lib.UsefulFunctions.stringUtils import *
import json

MAX_BUDGET = 400000
PASSWORD = "adminadmin"

def load_schools_classes():

    global GLV_SCHOOLID
    global ITIRR_SCHOOLID

    glv_classinfo = [
        (7,'702'),(7,'704'),(7,'706'),
        (10,'1002'),(10,'1006'),(10,'1007'),(10,'1008'),(10,'1009'),(10,'1010'),(10,'1011'),
        (12,'1201'),
     ]
    
    rr_classinfo = [
        (6,'601'),(6,'602'),(6,'603'),(6,'604'),(6,'605'),
        (7,'701'),(7,'702'),(7,'703'),(7,'704'),(7,'705'),
        (8,'801'),(8,'802'),(8,'803'),(8,'804'),
        (9,'901'),(9,'902'),(9,'903'),(9,'904'),
        (10,'1001'),(10,'1002'),(10,'1003'),(10,'1004'),(10,'1005'),
        (12,'1201'),
    ]
    
    school_list = [
        ('GLV','Guillermo Leon Valencia Colegio (sede integrado)','GLV (Integrado)', 'Calle 15A Nro 7 - 48','Duitama','Boyaca',glv_classinfo),
        ('ITIRR','Instituto Técnico Industrial Rafael Reyes', 'ITIRR', 'Carrera 18 # 23-116','Duitama','Boyaca',rr_classinfo),
    ]
    
    for school in school_list:
        myschool = School(
            schoolid = None, 
            schooldisplayname = school[1], 
            schoolabbreviation = school[2], 
            address = school[3], 
            city = school[4], 
            department = school[5]
        )
        
        # Create school
        myschoolid = myschool.save()[0]

        if(school[0] == "GLV"):
            GLV_SCHOOLID = myschoolid
        elif(school[0] == "ITIRR"):
            ITIRR_SCHOOLID = myschoolid

        # Save classes        
        for myclass in school[6]:
            mynewclass = Class(schoolid = myschoolid, classid = None, gradelevel = myclass[0], classdisplayname = myclass[1])
            mynewclass.save()

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

def load_all():
    
    # Clean out any existing schools
    delete_school(School(schoolid=1))
    delete_school(School(schoolid=2))

    load_schools_classes()
    load_users()
    load_rewards()
    
if (__name__ == '__main__'):
    load_all()