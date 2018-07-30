# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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
        return get_data(self, 'SP_DCPGetUser(%s,%s,%s)', (None, None, None))

    # Get info for one specific user
    def get_user(self, userid):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s)', (userid, None, None)) # Use tuple instead of array for input parameters

    # Lookup user for authentication (email / username)
    def get_user_auth(self, username = None, emailaddress = None):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s)', (None, username, emailaddress))

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

    def manage_display_info(self, myUser, actiontype):
        return save_data('SP_DCPManageUserDisplayInfo', (myUser.userid, actiontype,))[0]

    # TO-DO: possibly remove
    def add_event(self, myUser, eventid, contractid):
        return save_data('SP_DCPProcessUserEvent', (myUser.userid, eventid, contractid,))

    # TO-DO: possibly remove
    def add_notification(self, myUser, notificationid, contractid):
        return save_data('SP_DCPUpsertUserNotification', (myUser.userid, notificationid, contractid))

class UserReputationEventManager(models.Manager):
    
    def all(self):
        return self.get_events(None, None, None,)
    
    def get(self, eventid):
        return get_data_pk(self, 'SP_DCPGetUserReputationEvent(%s,%s,%s)', (None, None, eventid,))
    
    def get_events(self, userid = None, contractid = None, eventid = None):
        return get_data(self, 'SP_DCPGetUserReputationEvent(%s,%s,%s)', (userid, contractid, eventid,))
    
    def save(self, myUserReputationEvent):
        pass # Handled by user-level method

    def delete(self, myUserReputationEvent):
        pass # No use-case

class UserNotificationManager(models.Manager):
    
    def all(self):
        return self.get_notifications(None, None,)
    
    def get(self, notificationid):
        return get_data_pk(self, 'SP_DCPGetUserNotification(%s,%s,%s,%s,%s)', (None, None, notificationid, None, None))
    
    def get_notifications(self, userid = None, sourceeventid = None, notificationid = None, activeonlyflag = True, maxrows = None):
        return get_data(self, 'SP_DCPGetUserNotification(%s,%s,%s,%s,%s)', (userid, sourceeventid, notificationid, activeonlyflag, maxrows))
    
    def save(self, myUserNotification):
        pass # Handled by user-level method

    def delete(self, myUserNotification):
        pass # No use-case

class UserBadgeManager(models.Manager):
    
    def all(self):
        return self.get_badges(None, None,)
    
    def get(self, userid, badgeid):
        return get_data_pk(self, 'SP_DCPGetUserBadge(%s,%s)', (userid, badgeid))
    
    def get_badges(self, userid = None, badgeid = None ):
        return get_data(self, 'SP_DCPGetUserBadge(%s,%s)', (userid, badgeid,))
    
    def save(self, myUserBadge):
        pass # Handled by user-level method
        
    def delete(self, myUserBadge):
        pass # No use-case

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
    reputationvaluelastseents = models.DateTimeField()
    is_active = models.BooleanField()

    # Define data manager
    objects = MyUserManager()
    
    # Class info
    class Meta:
        managed = False # Ensure Django doesn't "manage" the table
        db_table = 'users' # Point to actual DB table
        
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
    
    def manage_display_info(self, actiontype):
        return MyUser.objects.manage_display_info(self, actiontype)
        
    # TO-DO: possibly remove
    def add_event(self, eventid, contractid = None):
        return MyUser.objects.add_event(self, eventid, contractid)
        
    # TO-DO: possibly remove
    def add_notification(self, notificationid, contractid = None):
        return MyUser.objects.add_notification(self, notificationid, contractid)
        
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

class UserReputationEvent(models.Model):
    
    eventid = models.BigIntegerField(primary_key=True)
    userid = models.IntegerField()
    sourceeventid = models.IntegerField()
    contractid = models.IntegerField()
    pointvalue = models.IntegerField(verbose_name="Puntos")
    eventts = models.DateTimeField(verbose_name="Fecha")
    eventdisplayname = models.CharField(max_length=100,verbose_name="Evento")
    
    class Meta:
        managed = False
        
    objects = UserReputationEventManager()
    
    def save(self):
        return UserReputationEvent.objects.save(self)
    
    def delete(self):
        return UserReputationEvent.objects.delete(self)

class UserNotification(models.Model):
    
    userid = models.IntegerField(primary_key=True)
    notificationid = models.BigIntegerField()
    notificationts = models.DateTimeField()
    notificationseen = models.BooleanField()
    notificationtext = models.CharField(max_length=500)
    contractid = models.IntegerField()
    sourceeventid = models.IntegerField()
    
    class Meta:
        managed = False
        
    objects = UserNotificationManager()
    
    def save(self):
        return UserNotification.objects.save(self)
    
    def delete(self):
        return UserNotification.objects.delete(self)

class UserBadge(models.Model):
    
    userid = models.IntegerField()
    badgeid = models.IntegerField(primary_key=True)
    badgelevel = models.CharField(max_length=1,verbose_name='Nivel')
    badgeshortname = models.CharField(max_length=50)
    badgedisplayname = models.CharField(max_length=50,verbose_name='Titulo')
    badgeachievedts = models.DateTimeField(verbose_name='Fecha')
    badgedescription = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    
    class Meta:
        managed = False
        
    objects = UserBadgeManager()
    
    def save(self):
        return UserBadge.objects.save(self)
    
    def delete(self):
        return UserBadge.objects.delete(self)