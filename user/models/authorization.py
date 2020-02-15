from django.db import models
from django.contrib.postgres.fields import ArrayField
from user.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.stringUtils import mychr

### MODEL MANAGERS ###
class ObjectManager(models.Manager):
    def all(self):
        return self.get_objects()
    
    def get(self, objectid, objectclass):
        return get_data_pk(self, 'SP_DCPGetObject(%s,%s)', (objectid, objectclass))
    
    def get_objects(self, objectid = None, objectclass = None):
        return get_data(self, 'SP_DCPGetObject(%s,%s)', (objectid, objectclass))

    def save(self, myObject):
        return save_data('SP_DCPUpsertObject', (
            myObject.objectid,
            myObject.objectclass,
            myObject.objectname
            )
        )[0] # Return objectid

    def delete(self, myObject):
        return delete_data('SP_DCPDeleteObject', (myObject.objectid, myObject.objectclass,))

class RoleManager(models.Manager):
    def all(self):
        return self.get_roles()
    
    def get(self, roleid):
        return get_data_pk(self, 'SP_DCPGetRole(%s)', (roleid,))

    def get_roles(self, roleid = None):
        return get_data(self, 'SP_DCPGetRole(%s)', (roleid,))
    
    def save(self, myRole):
        return save_data('SP_DCPUpsertRole', (
            myRole.roleid,
            myRole.name,
            myRole.description,
            myRole.publicflag,
            myRole.schoollist,
            myRole.usertypelist,
            myRole.userlist
            )
        )[0] # Return ID
    
    def delete(self, myRole):
        return delete_data('SP_DCPDeleteRole', (myRole.roleid,))

class RoleACLManager(models.Manager):
    def all(self):
        return self.get_role_acls()
    
    def get(self, roleid, objectid, objectclass):
        return get_data_pk(self, 'SP_DCPGetRoleACL(%s,%s,%s,%s)', (roleid, objectid, objectclass, None))
    
    def get_role_acls(self, roleid = None, objectid = None, objectclass = None, accesslevel = None):
        return get_data(self, 'SP_DCPGetRoleACL(%s,%s,%s,%s)', (roleid, objectid, objectclass, accesslevel))
    
    def save(self, myRoleACL):
        return save_data('SP_DCPUpsertRoleACL', (
            myRoleACL.roleid,
            myRoleACL.objectid,
            myRoleACL.objectclass,
            myRoleACL.accesslevel
            )
        )[0] # Return ID

    def delete(self, myRoleACL):
        return delete_data('SP_DCPDeleteRoleACL', (myRoleACL.roleid, myRoleACL.objectid, myRoleACL.objectclass))

### MODELS ###
class Object(MyModel):
    objectid = models.IntegerField(primary_key=True, verbose_name='ID')
    objectclass = models.CharField(max_length=2)
    objectname = models.CharField(max_length=100)
    
    objects = ObjectManager()

class Role(MyModel):
    
    roleid = models.IntegerField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    publicflag = models.BooleanField(verbose_name='General')
    schoollist = ArrayField(models.IntegerField())
    usertypelist = ArrayField(models.CharField(max_length=2))
    userlist = ArrayField(models.IntegerField())

    objects = RoleManager()
    
class RoleACL(Role, Object):
    
    id = models.IntegerField(primary_key=True) # dummy field
    
    objects = RoleACLManager()