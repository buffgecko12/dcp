# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from UsefulFunctions.dbUtils import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Data model managers (i.e. interface between DB and objects)

# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUserManager(BaseUserManager):

    # Create new user
    def create_user(self, password, username = None, usertype = None, firstname = None, lastname = None, defaultsignaturescanfile = None, phonenumber = None, emailaddress = None, reputationvalue = None):
 
        user = self.model(
            userid=None,
            username=username,
            usertype=usertype,
            firstname=firstname,
            lastname=lastname,
            defaultsignaturescanfile=defaultsignaturescanfile,
            phonenumber=phonenumber,
            emailaddress=emailaddress,
            reputationvalue = reputationvalue,
        )

        # Save hashed password
        user.set_password(password)

        # Save user data and update user object with newly created id
        result = user.save()
        user.userid = result[0] # TO-DO: Fix SP call

        return user

    def all(self):
        return get_data(self, 'SP_DCPGetUser(%s,%s,%s)', (None, None, None))

    # Get info for one specific user
    def get(self, userid):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s)', (userid, None, None)) # Use tuple instead of array for input parameters

    # Lookup user for authentication (email / username)
    def get_user_auth(self, username = None, emailaddress = None):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s)', (None, username, emailaddress))

    def save(self, myUser):
        return save_data('SP_DCPUpsertUser', 
            (
                myUser.userid,
                myUser.username,
                myUser.usertype,
                myUser.firstname,
                myUser.lastname,
                myUser.defaultsignaturescanfile,
                myUser.phonenumber,
                self.normalize_email(myUser.emailaddress),
                myUser.password,
                myUser.reputationvalue,
                myUser.last_login,
            )
         )
    
    def delete(self, myUser):
        return delete_data('SP_DCPDeleteUser', (myUser.userid,))

# Data models (i.e. tables)
# Create custom base user
# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUser(AbstractBaseUser):

    # Define attributes (inherited class includes password + last_login fields)
    userid = models.IntegerField(primary_key=True) # Specify as PK to prevent Django from creating "id" column and for queryset returns (raw)
    username = models.CharField(max_length=50, unique=True)
    usertype = models.CharField(max_length=1)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    defaultsignaturescanfile = models.BinaryField # TO-DO: Verify returns data properly in "get" functions
    phonenumber = models.CharField(max_length=25)
    emailaddress = models.CharField(max_length=250, unique=True)
    reputationvalue = models.IntegerField

    # Define data manager
    objects = MyUserManager()
    
    # Create new constructor (must be passed in correct order) -- i.e. inherited columns first)
    def __init__(self, password = None, last_login = None, userid = None, username = None, usertype = None, firstname = None, lastname = None, defaultsignaturescanfile = None, phonenumber = None, emailaddress = None, reputationvalue = None):
        
        # Call parent's init function
        super(get_user_model(), self).__init__()
        
        # Set properties
        self.userid = userid
        self.username = username
        self.usertype = usertype
        self.firstname = firstname
        self.lastname = lastname
        self.defaultsignaturescanfile = defaultsignaturescanfile
        self.phonenumber = phonenumber
        self.emailaddress = emailaddress
        self.reputationvalue = reputationvalue
        self.last_login = last_login
        self.password = password

    # Class info
    class Meta:
        managed = False # Ensure Django doesn't "manage" the table
        db_table = 'users' # Point to actual DB table
        
    # Required fields
    USERNAME_FIELD = 'userid' # specify how Django recognizes the user
    EMAIL_FIELD = 'emailaddress'
    REQUIRED_FIELDS = ['usertype','username','firstname','lastname'] # Fields required when creating a user interactively (email and password are included by default)

    # Methods
    def __str__(self):
        return self.firstname + " " + self.lastname
    
    def save(self):
        return MyUser.objects.save(self)

    def delete(self):
        return MyUser.objects.delete(self)
    
    def is_admin(self):
        if(self.usertype == 'A' or self.usertype == 'S'):
            return True
        else:
            return False

    def is_superuser(self):
        if(self.usertype == 'S'):
            return True
        else:
            return False
