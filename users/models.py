# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from UsefulFunctions.dbUtils import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Data model managers (i.e. interface between DB and objects)

# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUserManager(BaseUserManager):

    # Create new user
    def create_user(self, password, usertype = None, firstname = None, lastname = None, signaturescanfile = None, phonenumber = None, emailaddress = None):
 
        user = self.model(
            userid=None,
            usertype=usertype,
            firstname=firstname,
            lastname=lastname,
            signaturescanfile=signaturescanfile,
            phonenumber=phonenumber,
            emailaddress=emailaddress
        )

        # Save hashed password
        user.set_password(password)

        # Save user data and update user object with newly created id
        result = user.save() # TO-DO: Look at using existing save() function instead
        user.userid = result[0] # TO-DO: Fix SP call

        return user

    def get_all(self):
        return get_data(self, 'SP_DCPGetUser(%s)', (None,)) # Use tuple instead of array for input parameters

    # Get info for one specific user
    def get_user(self, userid):
        return get_data_pk(self, 'SP_DCPGetUser(%s)', (userid,)) # Use tuple instead of array for input parameters

    def save_user(self, myUser):
        return save_data('SP_DCPUpsertUser', 
            (
                myUser.userid,
                myUser.usertype,
                myUser.firstname,
                myUser.lastname,
                myUser.signaturescanfile,
                myUser.phonenumber,
                self.normalize_email(myUser.emailaddress),
                myUser.password,
                myUser.last_login,
            )
         )
    
    def delete_user(self, myUser):
        return delete_data('SP_DCPDeleteUser', (myUser.userid, None))

# Data models (i.e. tables)
# Create custom base user
# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUser(AbstractBaseUser):

    # Define attributes (inherited class includes password + last_login fields)
    userid = models.IntegerField(primary_key=True) # Specify as PK to prevent Django from creating "id" column and for queryset returns (raw)
    usertype = models.CharField(max_length=1)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    signaturescanfile = models.BinaryField # TO-DO: Verify returns data properly in "get" functions
    phonenumber = models.CharField(max_length=25)
    emailaddress = models.CharField(max_length=250)

    # Define data manager
    objects = MyUserManager()
    
    # Create new constructor (must be passed in correct order) -- i.e. inherited columns first)
    def __init__(self, password = None, last_login = None, userid = None, usertype = None, firstname = None, lastname = None, signaturescanfile = None, phonenumber = None, emailaddress = None):
        
        # Call parent's init function
        super(get_user_model(), self).__init__()
        
        # Set properties
        self.userid = userid
        self.usertype = usertype
        self.firstname = firstname
        self.lastname = lastname
        self.signaturescanfile = signaturescanfile
        self.phonenumber = phonenumber
        self.emailaddress = emailaddress
        self.last_login = last_login
        self.password = password

    # Class info
    class Meta:
        managed = False # Ensure Django doesn't "manage" the table
        db_table = 'users' # Point to actual DB table
        
    # Required fields
    USERNAME_FIELD = 'userid' # specify how Django recognizes the user
    EMAIL_FIELD = 'emailaddress'
    REQUIRED_FIELDS = ['usertype','firstname','lastname'] # Fields required when creating a user interactively (email and password are included by default)

    # Methods
    def __str__(self):
        return self.lastname
    
    def save(self):
        return MyUser.objects.save_user(self)

    def delete(self):
        return MyUser.objects.delete_user(self)
    
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
