# Model field names must match database column names for "Raw" queries to match fields properly

from django.db import models
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.emailUtils import send_email
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField, JSONField

from user.models.base import MyModel

from wakemeup.models.environment import File

from dotmap import DotMap

# Don't override default methods (get, all, save, delete) to avoid clashing with Django authentication
class MyUserManager(BaseUserManager):

    # Create new user
    def create_user(self, password, schoolid=None, username=None, usertype=None, firstname=None, lastname=None, emailaddress=None, sharedaccountflag=False):
 
        user = self.model(
            userid = None,
            schoolid = schoolid,
            username = username,
            usertype = usertype,
            firstname = firstname,
            lastname = lastname,
            emailaddress = emailaddress,
            sharedaccountflag = sharedaccountflag
        )

        # Save hashed password
        user.set_password(password)

        # Save user data and update user object with newly created id
        result = user.save_user()
        user.userid = result

        return user

    def all(self):
        return get_data(self, 'SP_DCPGetUser(%s,%s,%s,%s)', (None, None, None, None))

    # Get info for one specific user
    def get_user(self, userid, activeflag = None):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s,%s)', (userid, None, None, activeflag))

    # Lookup user for authentication (email / username)
    def get_user_auth(self, username = None, emailaddress = None):
        return get_data_pk(self, 'SP_DCPGetUser(%s,%s,%s,%s)', (None, username, emailaddress, None))

    def save_user(self, myUser):
        return save_data('SP_DCPUpsertUser', 
            (
                myUser.userid,
                myUser.schoolid,
                myUser.username,
                myUser.usertype,
                myUser.firstname,
                myUser.lastname,
                self.normalize_email(myUser.emailaddress),
                myUser.password,
                myUser.profilepictureid,
                myUser.sharedaccountflag,
                myUser.last_login,
            )
         )[0] # Return userid
    
    def delete(self, myUser):
        return delete_data('SP_DCPDeleteUser', (myUser.userid,))

    def manage_display_info(self, myUser, actiontype, notificationtype):
        mydata = save_data('SP_DCPManageUserDisplayInfo', (myUser.userid, actiontype, notificationtype, ))
        
        return ({
            'reputationvaluedelta':mydata[0],
            'opennotificationsflag':mydata[1],
            'profilepicturefile':mydata[2]
        })

    def check_access(self, myUser, objectid, objectclass, requestedaccesslevel, objectpermissionsflag):
        return get_data(self, 'SP_DCPCheckUserObjectAccess(%s,%s,%s,%s,%s)', (myUser.userid, objectid, objectclass, requestedaccesslevel, objectpermissionsflag))

    def add_event(self, myUser, eventid, contractid):
        return save_data('SP_DCPProcessUserEvent', (myUser.userid, eventid, contractid,))

    def add_notification(self, myUser, notificationid, contractid):
        return save_data('SP_DCPUpsertUserNotification', (myUser.userid, notificationid, contractid))

    def get_profile_picture_options(self, userid):
        pictures = get_data(self, 'SP_DCPGetUserProfilePicture(%s)', (userid,))

        # Add default "N/A" option
        picture_options = [(0,None)]
        
        for mypicture in pictures:
            picture_options.append(
                (
                    str(mypicture.profilepictureid), 
                    str(mypicture.profilepicturefilepath + mypicture.profilepicturefilename)
                )
            )
        
        return picture_options

    def send_email(self, myUser, email_subject, email_body):
        
        # Send e-mail (if address exists)
        if(myUser.emailaddress):
            send_email(subject=email_subject, body=email_body, to_list=[myUser.emailaddress,])

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

    # Define attributes (inherited class includes password + last_login fields)
    userid = models.IntegerField(primary_key=True) # Specify as PK to prevent Django from creating "id" column and for queryset returns (raw)
    schoolid = models.IntegerField()
    username = models.CharField(max_length=50, unique=True)
    usertype = models.CharField(max_length=2)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    emailaddress = models.CharField(max_length=250)
    profilepictureid = models.IntegerField()
    reputationvalue = models.IntegerField()
    reputationvaluelastseents = models.DateTimeField()
    sharedaccountflag = models.BooleanField()
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
    
    def manage_display_info(self, actiontype, notificationtype = None):
        return MyUser.objects.manage_display_info(self, actiontype, notificationtype)
        
    def check_access(self, objectid, objectclass, requestedaccesslevel=4, objectpermissionsflag=False):
        return MyUser.objects.check_access(self, objectid, objectclass, requestedaccesslevel, objectpermissionsflag)
    
    # Helper function to check permissions from an "auth" object
    def check_access_auth(self, auth, objectname, requestedaccesslevel):
        result = False
        myaccesslevel = auth.get(objectname, {}).get('accesslevel')

        if myaccesslevel:
            if (myaccesslevel >= requestedaccesslevel):
                result = True 

        return result

    def get_object_auth(self):
        myobjects = self.check_access(objectid=None, objectclass='BO', requestedaccesslevel=None)
        
        result = {}
        
        for myobject in myobjects:
            result.update({
                myobject.objectname: {'accesslevel': myobject.accesslevel}
            })

        return DotMap(result)

    def get_site_auth(self):
        
        DISABLE = {'disable':True}
        DISABLE_ADMINONLY = {'disable': True if not self.is_admin() else False}
        DISABLE_SHAREDACCOUNT = {'disable': True if self.sharedaccountflag else False}
        
        objectauth = self.get_object_auth()
        
        auth = {
            # Default permissions
            'objects': objectauth,
            
            # Navbar
            'navbar': {
                'admin': {
                    'permissions':{**DISABLE},
                    'syncgd':{**DISABLE_ADMINONLY},
                    **DISABLE_ADMINONLY,
                },
                'contracts':{**DISABLE},
                'reputation': {**DISABLE},
                'notifications': {**DISABLE},
                'files': {
                    'upload': {**DISABLE_ADMINONLY},
                    'manage': {**DISABLE_ADMINONLY},
                    }
                },
            
            # My Account
            'myaccount': {
                'profile': {**DISABLE_SHAREDACCOUNT},
                'tools': {**DISABLE_SHAREDACCOUNT},
                'reputation': {**DISABLE},
                'badges': {**DISABLE},
            },
        }
        
        return DotMap(auth)
    
    def add_event(self, eventid, contractid = None):
        return MyUser.objects.add_event(self, eventid, contractid)
        
    def add_notification(self, notificationid, contractid = None):
        return MyUser.objects.add_notification(self, notificationid, contractid)
        
    def send_email(self, email_subject = None, email_body = None):
        return MyUser.objects.send_email(self, email_subject, email_body)

    def get_files(self, accesslevel=4, hierarchyflag=False, objectpermissionsflag=False, **kwargs):
        return File.objects.get_files(hierarchyflag=hierarchyflag, accessinfo={'userid':self.userid, 'requestedaccesslevel':accesslevel, 'objectpermissionsflag':objectpermissionsflag}, **kwargs)

    def is_admin(self):
        if(self.usertype == 'AD' or self.usertype == 'SU'):
            return True
        else:
            return False

    def is_superuser(self):
        if(self.usertype == 'SU'):
            return True
        else:
            return False

class UserReputationEvent(MyUser, MyModel):
    
    eventid = models.BigIntegerField(primary_key=True)
    sourceeventid = models.IntegerField()
    contractid = models.IntegerField()
    pointvalue = models.IntegerField(verbose_name="Puntos")
    eventts = models.DateTimeField(verbose_name="Fecha")
    eventdisplayname = models.CharField(max_length=100,verbose_name="Evento")
    
    objects = UserReputationEventManager()
    
class UserNotification(MyUser, MyModel):
    
    notificationid = models.BigIntegerField(primary_key=True)
    notificationts = models.DateTimeField()
    notificationseen = models.BooleanField()
    notificationtext = models.CharField(max_length=500)
    contractid = models.IntegerField()
    sourceeventid = models.IntegerField()
    
    objects = UserNotificationManager()
    
class UserBadge(MyUser, MyModel):
    
    badgeid = models.IntegerField(primary_key=True)
    badgelevel = models.CharField(max_length=1,verbose_name='Nivel')
    badgeshortname = models.CharField(max_length=50)
    badgedisplayname = models.CharField(max_length=50,verbose_name='Titulo')
    badgeachievedts = models.DateTimeField(verbose_name='Fecha')
    badgedescription = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    profilepicturefilepath = models.CharField(max_length=250)
    profilepicturefilename = models.CharField(max_length=250)
    
    objects = UserBadgeManager()