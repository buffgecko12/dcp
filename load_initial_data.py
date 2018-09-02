# -*- coding: utf-8 -*-
import test.test_setup
from django.contrib.auth import get_user_model
from wakemeup.models.environment import School, Teacher, Class, Student
from wakemeup.models.contract import Reward
from lib.UsefulFunctions.stringUtils import mychr
import json

MAX_BUDGET = 500000
PASSWORD = "adminadmin"

def normalize_field(mystring):
    return mystring.replace(" ","").lower()

def create_user(usertype, schoolid, firstname,lastname,userrole):
    newuser = get_user_model().objects.create_user(
        password = PASSWORD, 
        usertype = usertype,
        schoolid = schoolid,
        firstname = firstname, 
        lastname = lastname, 
        username = normalize_field(firstname), 
        emailaddress = normalize_field(firstname) + '@' + normalize_field(lastname) + '.com', 
        userrole = userrole
    )
    
    return newuser

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
        myschoolid = myschool.save()

        if(school[0] == "GLV"):
            GLV_SCHOOLID = myschoolid
        elif(school[0] == "ITIRR"):
            ITIRR_SCHOOLID = myschoolid

        # Save classes        
        for myclass in school[6]:
            mynewclass = Class(schoolid = myschoolid, classid = None, gradelevel = myclass[0], classdisplayname = myclass[1])
            mynewclass.save()

def load_users():
    admin_list = [
        ('AD', None, 'admin','admin','S'),
    ]

    for admin in admin_list:
        create_user(admin[0], admin[1], admin[2], admin[3], admin[4])

    teacher_list = [        
         ('Chris','Khosravi',GLV_SCHOOLID,['1201'],),
    ]

    for teacher in teacher_list:
        myclassinfo = {'currentclasses':[]}
        myschoolid = teacher[2]

        myuser = create_user('TR', myschoolid, teacher[0], teacher[1], 'U')

        # Convert class name list to classid list
        for myclass in teacher[3]:
            myclassid = Class.objects.get_classes(schoolid = myschoolid, classdisplayname = myclass)[0].classid
            myclassinfo['currentclasses'].append({'classid':myclassid})
        
        # Assign teacher classes
        myteacher = Teacher(
            teacheruserid = myuser.userid,
            schoolid = myschoolid,
            classinfo = json.dumps(myclassinfo),
            firstname = myuser.firstname,
            lastname = myuser.lastname,
            emailaddress = myuser.emailaddress,
            phonenumber = myuser.phonenumber,
            defaultsignaturescanfile = myuser.defaultsignaturescanfile
        )
        
        # Save teacher info
        myteacher.save()
        myteacher.update_budget(maxbudget = MAX_BUDGET)

    student_list = [
        ('Roger','Federer',ITIRR_SCHOOLID,'1201'),        
        ('Rafael','Nadal',ITIRR_SCHOOLID,'1201'),        
        ('Steffi','Graf',ITIRR_SCHOOLID,'1201'),        
        ('Angelique','Kerber',ITIRR_SCHOOLID,'1201'),        
        ('Roberto','Clemente',GLV_SCHOOLID,'1201'),        
        ('Hank','Aaron',GLV_SCHOOLID,'1201'),        
        ('Nelson','Mandela',GLV_SCHOOLID,'1201'),        
        ('Jackie','Robinson',GLV_SCHOOLID,'1201'),        
    ]

    for student in student_list:

        myuser = create_user('ST', student[2], student[0], student[1], 'U')
        myclassid = Class.objects.get_classes(schoolid = student[2], classdisplayname = student[3])[0].classid

        # Assign student class / info
        mystudent = Student(
            studentuserid = myuser.userid,
            schoolid = myuser.schoolid,
            classid = myclassid,
            firstname = myuser.firstname,
            lastname = myuser.lastname,
            emailaddress = myuser.emailaddress,
            phonenumber = myuser.phonenumber,
            defaultsignaturescanfile = myuser.defaultsignaturescanfile
        )
        
        mystudent.save()

def load_rewards():
    reward_list = [
        ('Tiquete al cine', 'Tiquete al cine en Innovo.', 6000),
        ('Pizza', 'Pizza y gaseosa.', 5000),
        ('Hamburguesa', 'Hamburguesa y gaseoas.', 5000),
        ('Guatika', 'Tiquete a Guatika.', 25000),
        ('B' + mychr('a') + 'lon de f' + mychr('u') + 'tbol', 'B' + mychr('a') + 'lon de f' + mychr('u') + 'tbol', 15000)
    ]

    for reward in reward_list:
        myreward = Reward(
            rewardid = None,
            rewarddisplayname = reward[0],
            rewarddescription = reward[1],
            rewardvalue = reward[2],
            createdbyuserid = 0, 
        )
        
        myreward.save(globalflag = True)

def load_all():
    # Clean out any existing schools
    School(schoolid=1).delete()
    School(schoolid=2).delete()

    load_schools_classes()
    load_users()
    load_rewards()
    
if (__name__ == '__main__'):
    load_all()