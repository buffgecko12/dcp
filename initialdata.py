from lib.UsefulFunctions.googleUtils import GoogleDrive, get_gd_locator
from lib.UsefulFunctions.envUtils import check_env
from lib.UsefulFunctions.stringUtils import mychr

# Non-configurable parameters
INCENTIVE_PROGRAM = 'incentive'

# Configurable parameters
DEFAULT_MAX_BUDGET = 10000
DEFAULT_PASSWORD = "somepassword"
CREATE_CALENDAR_FLAG = False

# Initial data
YEARS_LIST = [2018, 2019, 2020]

# User types: SU - Super user, SA - Site admin, AD - Program Admin, TR - teacher, ST - student, SF - school staff, OT - other
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
        "department":"Some department",
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
    'admintools':{'objectclass':'VW','objectname':'admintools'},
    'program':{'objectclass':'BO','objectname':'program'}, # 2.0.1
}

ROLE_LIST = {

    # User roles
    'role_public':{'roleclass':'US','name':'Public','description':'All users','publicflag':True},
    'role_super_user':{'roleclass':'US','name':'Super user','description':'Full access','usertypelist':['SU']},
    'role_site_admin':{'roleclass':'US','name':'Site Administrator','description':'Access to administer site','usertypelist':['SA']},
    'role_admin':{'roleclass':'US','name':'Site Admins (Super User and Site Administrator)','description':'Access to administer site','usertypelist':['SA','SU']},
    'role_buyer':{'roleclass':'US','name':'Buyer','description':'Comprador','usertypelist':['BR']},
    'role_teacher':{'roleclass':'US','name':'Teacher','description':'Teachers','usertypelist':['TR']},
    'role_staff':{'roleclass':'US','name':'Staff','description':'School staff','usertypelist':['SF']},
    'role_program_admin':{'roleclass':'PG','name':'Program Administrator','description':'Program administrator (i.e. buyer, coordinator)','usertypelist':['AD']},
    'role_program_coordinator':{'roleclass':'PG','name':'Program Coordinator','description':'Coordinate program at a school (usually a teacher)'},
    'role_program_purchaser':{'roleclass':'PG','name':'Program Purchaser','description':'Cordinate purchase and delivery of incentives'},
    
    # Object roles
    # General
    'role_get_general':{'roleclass':'PG','name':'General - View','description':'Read access on general program items','usertypelist':['TR']},
    'role_edit_general':{'roleclass':'PG','name':'General - Edit','description':'Edit access on general program items'},
    'role_delete_general':{'roleclass':'PG','name':'General - Delete','description':'Delete access on general program items','usertypelist':['SU','SA']},
    
    # Files
    'role_get_file':{'roleclass':'FL','name':'File - View','description':'Read/download access on files','publicflag':True},
    'role_create_file':{'roleclass':'FL','name':'File - Create','description':'Create access on files'},
    'role_delete_file':{'roleclass':'FL','name':'File - Delete','description':'Delete access on files','usertypelist':['SU','SA']},
    
    # Calendar
    'role_get_calendar':{'roleclass':'OT','name':'Calendar - View','description':'Read access on calendar','publicflag':True},

    # Contract
    'role_get_contract':{'roleclass':'PG','name':'Contract - View','description':'Read access on contracts','usertypelist':['ST']},
    'role_create_contract':{'roleclass':'PG','name':'Contract - Create','description':'Create access on contracts','usertypelist':['TR','SA']},
    'role_delete_contract':{'roleclass':'PG','name':'Contract - Delete','description':'Delete access on contracts','usertypelist':['SU']},
    
    # Program (2.0.1)
    'role_get_program':{'roleclass':'PG','name':'Program - View','description':'Read/download access on program info','usertypelist':['TR']},
    'role_edit_program':{'roleclass':'PG','name':'Program - Edit','description':'Edit access on program info'},
    'role_create_program':{'roleclass':'PG','name':'Program - Create','description':'Create access on program info','usertypelist':['SA']},
    'role_delete_program':{'roleclass':'PG','name':'Program - Delete','description':'Delete access on program info','usertypelist':['SU']},
}

GENERAL_OBJECTS = ['school','class','contract','reward','teacher']

# Default ACLs
ACL_LIST = {

    # DEFAULT PERMISSIONS
    # General
    'role_get_general': [{"object":myobject,"accesslevel":4} for myobject in GENERAL_OBJECTS], # General view access (teacher)
    'role_delete_general': [{"object":myobject,"accesslevel":12} for myobject in GENERAL_OBJECTS], # General delete access (super user, site admin)

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

    # Program (2.0.1)
    'role_get_program':[{'object':'program','accesslevel':4}],
    'role_edit_program':[{'object':'program','accesslevel':8}],
    'role_create_program':[{'object':'program','accesslevel':10}],
    'role_delete_program':[{'object':'program','accesslevel':12}],
    
    # CUSTOM PERMISSIONS
    # Public
    'role_public': [
        {'object':'user',"accesslevel":8},
        {'object':'reward',"accesslevel":1},
    ],

    # Buyer
    'role_buyer':[
        {'object':'file','accesslevel':10}, # Buyer (upload files)
    ],

    # Admin
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
