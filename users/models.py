# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from lib.UsefulFunctions.dbUtils import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Data model managers (i.e. interface between DB and objects)

# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUserManager(BaseUserManager):

    # Create new user
    def create_user(self, password, username = None, usertype = None, firstname = None, lastname = None, defaultsignaturescanfile = None, phonenumber = None, emailaddress = None, userrole = None):
 
        user = self.model(
            userid=None,
            username=username,
            usertype=usertype,
            firstname=firstname,
            lastname=lastname,
            defaultsignaturescanfile=defaultsignaturescanfile,
            phonenumber=phonenumber,
            emailaddress=emailaddress,
            userrole=userrole,
        )

        # Save hashed password
        user.set_password(password)

        # Save user data and update user object with newly created id
        result = user.save_user()
        user.userid = result

        return user

    def all(self):
        return get_data(self, 'DCPViews.SP_DCPGetUser(%s,%s,%s)', (None, None, None))

    # Get info for one specific user
    def get_user(self, userid):
        return get_data_pk(self, 'DCPViews.SP_DCPGetUser(%s,%s,%s)', (userid, None, None)) # Use tuple instead of array for input parameters

    # Lookup user for authentication (email / username)
    def get_user_auth(self, username = None, emailaddress = None):
        return get_data_pk(self, 'DCPViews.SP_DCPGetUser(%s,%s,%s)', (None, username, emailaddress))

    def save_user(self, myUser):
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
                myUser.userrole,
                myUser.last_login,
            )
         )[0] # Return userid
    
    def delete(self, myUser):
        return delete_data('SP_DCPDeleteUser', (myUser.userid,))

    def deactivate(self, myUser):
        return save_data('SP_DCPDeactivateUser', (myUser.userid,))

# Data models (i.e. tables)
# Create custom base user
# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUser(AbstractBaseUser):

    usertype_choices = [
        ('AD','Administrador de programa'),
        ('SF','Administrador de colegio'),
        ('TR','Docente'),
        ('ST','Estudiante'),
        ('OT','Otro'),
    ]

    # Define attributes (inherited class includes password + last_login fields)
    userid = models.IntegerField(primary_key=True) # Specify as PK to prevent Django from creating "id" column and for queryset returns (raw)
    username = models.CharField(max_length=50, unique=True)
    usertype = models.CharField(max_length=2, choices=usertype_choices)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    defaultsignaturescanfile = models.BinaryField()
    phonenumber = models.CharField(max_length=25)
    emailaddress = models.CharField(max_length=250)
    userrole = models.CharField(max_length=1)
    reputationvalue = models.IntegerField()
    is_active = models.BooleanField()

    # Define data manager
    objects = MyUserManager()
    
    # Class info
    class Meta:
        managed = False # Ensure Django doesn't "manage" the table
        db_table = 'DCPViews.users' # Point to actual DB table
        
    # Required fields
    USERNAME_FIELD = 'username' # specify how Django recognizes the user
    EMAIL_FIELD = 'emailaddress'
    REQUIRED_FIELDS = ['usertype','firstname','lastname'] # Fields required when creating a user interactively (email and password are included by default)

    # Methods
    def __str__(self):
        return self.firstname + " " + self.lastname
    
    # Use "save_user()" instead of "save()" to allow auth views to work
    def save_user(self):
        return MyUser.objects.save_user(self)

    def delete(self):
        return MyUser.objects.delete(self)

    def deactivate(self):
        return MyUser.objects.deactivate(self)
        
    def is_admin(self):
        if(self.userrole == 'A' or self.userrole == 'S'):
            return True
        else:
            return False

    def is_superuser(self):
        if(self.userrole == 'S'):
            return True
        else:
            return False

class UserReputationEventManager(models.Manager):
    
    def all(self):
        return self.get_events(None, None, None,)
    
    def get(self, eventid):
        return get_data_pk(self, 'SP_DCPGetUserReputationEvent(%s,%s,%s)', (None, None, eventid,))
    
    def get_events(self, userid, contractid, eventid):
        return get_data(self, 'SP_DCPGetUserReputationEvent(%s,%s,%s)', (userid, contractid, eventid,))
    
    def save(self, myUserReputationEvent):
        return save_data('SP_DCPUpsertUserReputationEvent', 
             (
                myUserReputationEvent.userid,
                myUserReputationEvent.eventtype,
                myUserReputationEvent.eventts,
                myUserReputationEvent.pointvalue,
                myUserReputationEvent.contractid
            )
        )[0] # Return eventid
        
    def delete(self, myUserReputationEvent):
        pass # No use-case
    
class UserReputationEvent(models.Model):
    
    eventid = models.BigIntegerField(primary_key=True)
    userid = models.IntegerField()
    eventtype = models.CharField(max_length=2)
    eventts = models.DateTimeField()
    pointvalue = models.IntegerField()
    contractid = models.IntegerField()
    
    class Meta:
        managed = False
        
    objects = UserReputationEventManager()
    
    def save(self):
        return UserReputationEvent.objects.save(self)
    
    def delete(self):
        return UserReputationEvent.objects.delete(self)