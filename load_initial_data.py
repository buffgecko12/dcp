# -*- coding: utf-8 -*-
import test.test_setup
from django.contrib.auth import get_user_model
from wakemeup.models.environment import School, Teacher, Class, Student
from wakemeup.models.contract import Reward
from lib.UsefulFunctions.stringUtils import mychr
import json

PASSWORD = 'adminadmin'
MAX_BUDGET = 500000

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
        '701','702','703','704','705','706',
        '801','802','809','810','811','812',
        '901', '902', '903', '904', '905', '906', '907', '908', '909', '910', '911', '912', \
        '1001','1002','1003','1004','1005','1006','1007','1008','1009','1010','1011', \
        '1101','1102','1103','1104','1105','1106','1107','1108','1109','1110','1111'
     ]
    
    rr_classinfo = ['601','602','707','708','801','1201']
    
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
            mynewclass = Class(schoolid = myschoolid, classid = None, classdisplayname = myclass)
            mynewclass.save()

def load_users():
    admin_list = [
        ('AD', None, 'Chris','Khosravi','S'),
        ('AD', None, 'Assir','Sandoval','A'),
        ('SF', GLV_SCHOOLID, 'Omaira-admin','Rincon','U'),
        ('SF', GLV_SCHOOLID, 'Gladys-admin','Piracon','U'),
    ]

    for admin in admin_list:
        create_user(admin[0], admin[1], admin[2], admin[3], admin[4])

    teacher_list = [        

#         ('Suleima','Ferrer',GLV_SCHOOLID,['904','905','906'],),
#         ('Alba Nelly','Salamanca',GLV_SCHOOLID,['901','902','903','1006','1007'],),
#         ('Diana','Vera',GLV_SCHOOLID,['1004','1005','1101','1102','1103'],),
#         ('Diego','Cruz',GLV_SCHOOLID,['701','702','703','704','705'],),
#         ('Clara','Sanchez',GLV_SCHOOLID,['907','908','909','910'],),
#         ('Adriana','Saenz',GLV_SCHOOLID,['1003','1108','1109','1110','1111'],),
#         ('Liliana','Lizarazo',GLV_SCHOOLID,['1001','1104','1105','1106','1107'],),
#         ('Lorena','Rojas',GLV_SCHOOLID,['1002','1008','1009','1010','1011'],),
#         ('Doris','Avella',GLV_SCHOOLID,['706'],),
#         ('Patricia','Conde',GLV_SCHOOLID,['911','912'],),
#         
        
        ('Suleima','Ferrer',GLV_SCHOOLID,['904'],),
        ('Alba Nelly','Salamanca',GLV_SCHOOLID,['901'],),
        ('Diana','Vera',GLV_SCHOOLID,['1102'],),
        ('Diego','Cruz',GLV_SCHOOLID,['701'],),
        ('Clara','Sanchez',GLV_SCHOOLID,['907'],),
        ('Adriana','Saenz',GLV_SCHOOLID,['1003'],),
        ('Liliana','Lizarazo',GLV_SCHOOLID,['1001'],),
        ('Lorena','Rojas',GLV_SCHOOLID,['1002'],),
        ('Doris','Avella',GLV_SCHOOLID,['706'],),
        ('Patricia','Conde',GLV_SCHOOLID,['911'],),

        ('Omaira','Rincon',GLV_SCHOOLID,['809'],),
        ('Gladys','Piracon',GLV_SCHOOLID,['811'],),

        
        ('Elizabeth','Moreno',ITIRR_SCHOOLID,['601','602','801','1201'],),
        ('David','TennisMachine',ITIRR_SCHOOLID,['707','708'],),
        
        
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
        
        ('Jesus David','Martinez',GLV_SCHOOLID,'901'),
        ('Juan Diego','Rodriguez',GLV_SCHOOLID,'901'),
        ('Juan Felipe','Quatana Vargas',GLV_SCHOOLID,'901'),
        ('Meslan Santiago','Puesta Cajica',GLV_SCHOOLID,'901'),

        ('Daniel Esteban','Nino Mosquera',GLV_SCHOOLID,'904',),
        ('Dianni Brithey','Hoyos Camacho',GLV_SCHOOLID,'904',),
        ('Diego Andrey','Rueda Bayona',GLV_SCHOOLID,'904',),
        ('Emerson Javier','Perez',GLV_SCHOOLID,'904',),
        ('Jennifer Carolina','Galvis P',GLV_SCHOOLID,'904',),
        ('Johan Santiago','Solano',GLV_SCHOOLID,'904',),
#         ('Juan Diego','Bautista Corredor',GLV_SCHOOLID,'904',),

        ('Brayan Camilo','Sanchez Arenas',GLV_SCHOOLID,'911'),
        ('Jhony Esteban','Marchigo',GLV_SCHOOLID,'911'),
        ('Julian','Ballesteros',GLV_SCHOOLID,'911'),
        ('Karlheinz Alainthen','Moreno',GLV_SCHOOLID,'911'),

        ('Fabian Camilo','Anaya',GLV_SCHOOLID,'1102'),
        ('Valentina','Gaspar Baquero',GLV_SCHOOLID,'1102'),
        ('Henry Felipe','Olarte Salgado',GLV_SCHOOLID,'1102'),
        ('Lizeth Camila','Rivera Garcia',GLV_SCHOOLID,'1102'),
        
        ('Daniel Felipe','Triano',GLV_SCHOOLID,'907'),
        ('Deisy Marcela','Fonseca',GLV_SCHOOLID,'907'),
        ('Jerson David','Baquero',GLV_SCHOOLID,'907'),
        ('Eduard Sebastian','Carvajal Fuentes',GLV_SCHOOLID,'907'),

        ('Andrea Alexandra','Alvarez Manrique',GLV_SCHOOLID,'1001'),
        ('Andrea Yuliana','Gonzalez',GLV_SCHOOLID,'1001'),
        ('Nayelly Ximena','Rojas Torres',GLV_SCHOOLID,'1001'),
        ('Jhonatan David','Fajardo',GLV_SCHOOLID,'1001'),

        ('Aaron David','Quinonez',GLV_SCHOOLID,'1002'),
        ('Juan Camilo','Ramos Ruiz',GLV_SCHOOLID,'1002'),
        ('David ALejandro','Garcia Parra',GLV_SCHOOLID,'1002'),
        ('Eliana Tamara','Bautista',GLV_SCHOOLID,'1002'),

        ('Nancy Xiomara','Infante',GLV_SCHOOLID,'1003'),
        ('Brajhan Jhair','Ravelo',GLV_SCHOOLID,'1003'),
        ('Hugo Sebastian','Rojas Enciso',GLV_SCHOOLID,'1003'),
        ('Johan Estiban','Mojica Sepulveda',GLV_SCHOOLID,'1003'),

      
#         ('Alejandra','Pita',GLV_SCHOOLID,'905'),
        ('Claudio','Salamanca',GLV_SCHOOLID,'905'),
        ('Dana','Camargo Castro',GLV_SCHOOLID,'905'),
        ('Juan Sebastian','Corredor',GLV_SCHOOLID,'905'),
        ('Katerin Daniela','Cucunuba',GLV_SCHOOLID,'905'),
        ('Laura Sofia','Sandoval',GLV_SCHOOLID,'905'),
        ('Natalia Valentina','Rosas Gomez',GLV_SCHOOLID,'905'),
        ('Nathaly','Salazar',GLV_SCHOOLID,'905'),
        ('Paula','Ramos',GLV_SCHOOLID,'905'),
        
        # Diego - 701 (really Alba, 906)
        ('Cindy Valentina','Herrera Valderrama',GLV_SCHOOLID,'701'),
        ('Julieth Xiomara','Gonzalez',GLV_SCHOOLID,'701'),
        ('Juree Valentina','Gallo Santos',GLV_SCHOOLID,'701'),
        ('Maria Fernanda','Duarte',GLV_SCHOOLID,'701'),

        

        ('Angie Lorena','Marquez Lopez',GLV_SCHOOLID,'902'),
        ('Angie Natalia','Pinzon Sanabria',GLV_SCHOOLID,'902'),
        ('Angy Viviana','Moreno Gonzalez',GLV_SCHOOLID,'902'),
        ('Bresly Soledad','Sonabria',GLV_SCHOOLID,'902'),
        ('Jennifer Alexandra','Coronado Pinzon',GLV_SCHOOLID,'902'),
        
        ('Ana Fernanda','Gomez Camargo',GLV_SCHOOLID,'903'),
        ('Angela Johana','Acero Camargo',GLV_SCHOOLID,'903'),
        ('Angela Katherina','Macias',GLV_SCHOOLID,'903'),
        ('Angela Sofia','Perez',GLV_SCHOOLID,'903'),
        ('Angie Jolieth','Mayarga Juarez',GLV_SCHOOLID,'903'),
        
        ('Yessid','Maldonado',GLV_SCHOOLID,'1006'),
        ('Jose Alejandro','Pachecho Reyes',GLV_SCHOOLID,'1006'),
        ('Sergio Alexander','Gonzalez',GLV_SCHOOLID,'1006'),
        ('Luis Esteban','Benavides',GLV_SCHOOLID,'1006'),
#        ('Valentina','Gomez Blanco',GLV_SCHOOLID,'1006'),

        ('Andres Felipe','Chiuatu Parra',GLV_SCHOOLID,'1007'),
        ('Dennys Aleyda','Vargas',GLV_SCHOOLID,'1007'),
        ('Javier','Martinez Corredor',GLV_SCHOOLID,'1007'),
        ('Jhonatan','Montanez Cespedes',GLV_SCHOOLID,'1007'),
        ('Natalia Andrea','Cuervo Aranguren',GLV_SCHOOLID,'1007'),


        ('Juan Esteban','Cuervo',GLV_SCHOOLID,'801'),
        ('Sandra Milena','Pedraza',GLV_SCHOOLID,'801'),
        ('Catalina','Becerra',GLV_SCHOOLID,'801'),
        ('Laura Valentina','Parra',GLV_SCHOOLID,'801'),
        
        ('Farid','Martinez',GLV_SCHOOLID,'802'),
        ('Dennys','Estupinan',GLV_SCHOOLID,'802'),
        ('Leidy','Sandoval',GLV_SCHOOLID,'802'),

        ('Laura Camila','Merchan',GLV_SCHOOLID,'809'),
        ('Jorge Felipe','Rojas',GLV_SCHOOLID,'809'),
        ('Jaider Eliot','Blanco',GLV_SCHOOLID,'809'),
        ('Paula Alejandra','Garcia',GLV_SCHOOLID,'809'),

        ('Maria Camila','Cuervo',GLV_SCHOOLID,'811'),
        ('Brayan Esteban','Pardo',GLV_SCHOOLID,'811'),
        ('Alfonso Diego','Avendona',GLV_SCHOOLID,'811'),
        ('Luis Alejandro','Gonzalez',GLV_SCHOOLID,'811'),

        ('Laura Maria','Supelano',GLV_SCHOOLID,'1101'),
        ('Manuela','Bustamante',GLV_SCHOOLID,'1101'),
        ('Omar','Nino',GLV_SCHOOLID,'1101'),
        ('Karen Gisela','Sisa',GLV_SCHOOLID,'1103'),
        ('Karol Tatiana','Guevara',GLV_SCHOOLID,'1103'),
        ('Lizeth Paola','Martinez',GLV_SCHOOLID,'1103'),


        
        ('Yury','Galvan',ITIRR_SCHOOLID,'601'),
        ('Danna Valentina','Pedraza',ITIRR_SCHOOLID,'601'),
        ('Alejandra','Mora Cuspoca',ITIRR_SCHOOLID,'601'),
        ('Mary Tatiana','Avendano',ITIRR_SCHOOLID,'601'),
        
        ('Brayan Estiven','Parra',ITIRR_SCHOOLID,'602'),
        ('Brayan','Pardo',ITIRR_SCHOOLID,'602'),

        ('Juan Filipe','Merchan',ITIRR_SCHOOLID,'801'),
        ('Derly Yurany','Rojas',ITIRR_SCHOOLID,'801'),
        ('Jaider Alejandro','Lopez',ITIRR_SCHOOLID,'801'),
        ('Jorge Andres','Nino',ITIRR_SCHOOLID,'801'),

        # Doris - 706
        ('Angel Daniel','Camacho',GLV_SCHOOLID,'706'),
        ('Dorlian Yizeth','Quinones',GLV_SCHOOLID,'706'),
        ('Manuel Fernando','Vargas',GLV_SCHOOLID,'706'),
        ('Yimi Alexander','Pamplona',GLV_SCHOOLID,'706'),
        


        ('Christopher','Khosravi',ITIRR_SCHOOLID,'1201'),
        ('Fernando','Becerra',ITIRR_SCHOOLID,'1201'),

        ('Roger','Federer',ITIRR_SCHOOLID,'707'),
        ('Novak','Djokovic',ITIRR_SCHOOLID,'707'),
        ('Rafael','Nadal',ITIRR_SCHOOLID,'707'),
        ('Stefan','Edberg',ITIRR_SCHOOLID,'707'),
        ('Carolina','Wozniacki',ITIRR_SCHOOLID,'708'),
        ('Anna','Kournikova',ITIRR_SCHOOLID,'708'),
        ('Ana','Ivanovic',ITIRR_SCHOOLID,'708'),
        
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
        ('Tiquetes al cine', 'Tiquetes al cine en Innovo.', 6000),
        ('Pizza', 'Pizza y gaseosa.', 5000),
        ('Hamburguesa', 'Hamburguesa y gaseoas.', 5000),
        ('Guatika', 'Tiquete a Guatika.', 25000),
        ('B' + mychr('a') + 'lon de f' + mychr('u') + 'tbol', '', 15000)
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