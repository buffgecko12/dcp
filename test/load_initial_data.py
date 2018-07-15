# -*- coding: utf-8 -*-
import test.test_setup
from django.contrib.auth import get_user_model
from wakemeup.models.environment import School, Teacher, Class, Student
from wakemeup.models.contract import Reward
import json

PASSWORD = 'adminadmin'
MAX_BUDGET = 600000

def normalize_field(mystring):
    return mystring.replace(" ","").lower()

def create_user(usertype,firstname,lastname,userrole):
    newuser = get_user_model().objects.create_user(
        password = PASSWORD, 
        usertype = usertype,
        firstname = firstname, 
        lastname = lastname, 
        username = normalize_field(firstname), 
        emailaddress = normalize_field(firstname) + '@' + normalize_field(lastname) + '.com', 
        userrole = userrole
    )
    
    return newuser

def load_schools_classes():
    glv_classinfo = [
        '901', '902', '903', '904', '905', '906', '907', '908', '909', '910', '911', '912', \
        '1001','1002','1003','1004','1005','1006','1007','1008','1009','1010','1011', \
        '1101','1102','1103','1104','1105','1106','1107','1108','1109','1110','1111'
     ]
    
    rr_classinfo = []
    
    school_list = [
        (1, 'Guillermo Leon Valencia Colegio (sede integrado)','GLV (Integrado)', 'Calle 15A Nro 7 - 48','Duitama','Boyaca',glv_classinfo),
        (2, 'Instituto T�cnico Industrial Rafael Reyes', 'ITIRR', 'Carrera 18 # 23-116','Duitama','Boyaca',rr_classinfo),
    ]
    
    for school in school_list:
        myschool = School(
            schoolid = school[0], 
            schooldisplayname = school[1], 
            schoolabbreviation = school[2], 
            address = school[3], 
            city = school[4], 
            department = school[5]
        )
        
        # Create school
        myschoolid = myschool.save()

        # Save classes        
        for myclass in school[6]:
            mynewclass = Class(schoolid = myschoolid, classid = None, classdisplayname = myclass)
            mynewclass.save()

def load_users():
    admin_list = [
        ('AD', 'Chris','Khosravi','S'),
        ('AD', 'Assir','Sandoval','A'),
        ('SF', 'Omaira','Rincon','U'),
        ('SF', 'Gladys','Piracon','U'),
    ]

    for admin in admin_list:
        create_user(admin[0], admin[1], admin[2], admin[3])

    teacher_list = [        
        ('Suleima','Ferrer',1,['904','905','906'],),
        ('Alba Nelly','Salamanca',1,['901','902','903','1006','1007'],),
        ('Diana','Vera',1,['1004','1005','1101','1102','1103'],),
        ('Diego','Cruz',1,[],),
        ('Clara','Sanchez',1,['907','908','909','910'],),
        ('Adriana','Saenz',1,['1003','1108','1109','1110','1111'],),
        ('Liliana','Lizarazo',1,['1001','1104','1105','1106','1107'],),
        ('Lorena','Rojas',1,['1002','1008','1009','1010','1011'],),
        ('Doris','Avella',1,[],),
        ('Patricia','Conde',1,['911','912'],),
    ]

    for teacher in teacher_list:
        myclassinfo = {'currentclasses':[]}
        myschoolid = teacher[2]

        myteacheruserid = create_user('TR', teacher[0], teacher[1], 'U').userid

        # Convert class name list to classid list
        for myclass in teacher[3]:
            myclassid = Class.objects.get_classes(schoolid = myschoolid, classdisplayname = myclass)[0].classid
            myclassinfo['currentclasses'].append({'classid':myclassid})
        
        # Assign teacher classes
        myteacher = Teacher(
            teacheruserid = myteacheruserid,
            schoolid = myschoolid,
            classinfo = json.dumps(myclassinfo)
        )
        
        # Save teacher info
        myteacher.save()
        myteacher.update_budget(maxbudget = MAX_BUDGET)

    student_list = [
        ('Daniel Esteban','Nino Mosquera',1,'904',),
        ('Dianni Brithey','Hoyos Camacho',1,'904',),
        ('Diego Andrey','Rueda Bayona',1,'904',),
        ('Emerson Javier','Perez',1,'904',),
        ('Jennifer Carolina','Galvis P',1,'904',),
        ('Johan Santiago','Solano',1,'904',),
        ('Juan Diego','Bautista Corredor',1,'904',),
    ]

    for student in student_list:
        mystudentuserid = create_user('ST', student[0], student[1], 'U').userid
        myclassid = Class.objects.get_classes(schoolid = student[2], classdisplayname = student[3])[0].classid

        # Assign student class / info
        mystudent = Student(
            studentuserid = mystudentuserid,
            classid = myclassid
        )
        
        mystudent.save()

def load_rewards():
    reward_list = [
        ('Tiquetes al cine', 'Tiquetes al cine en Innovo.', 6000),
        ('Pizza', 'Pizza y gaseosa.', 5000),
        ('Hamburguesa', 'Hamburguesa y gaseoas.', 5000),
        ('Guatika', 'Tiquete a Guatika.', 25000)
    ]

    for reward in reward_list:
        myreward = Reward(
            rewardid = None,
            rewarddisplayname = reward[0],
            rewarddescription = reward[1],
            rewardvalue = reward[2],
        )
        
        myreward.save(createdbyuserid = 0, globalflag = True)

def load_all():
    # Clean out any existing schools
    School(schoolid=1).delete()
    School(schoolid=2).delete()

    load_schools_classes()
    load_users()
    load_rewards()
    
if (__name__ == '__main__'):
    load_all()