from django.db import models
from django.contrib.postgres.fields import ArrayField
from user.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.dataUtils import *

### MODEL MANAGERS ###
class ObjectManager(models.Manager):
    def all(self):
        return self.get_objects()
    
    def get(self, objectid, objectclass):
        return get_data_pk(self, 'SP_DCPGetObject(%s,%s,%s)', (objectid, objectclass, None))
    
    def get_objects(self, objectid = None, objectclass = None, objectname = None):
        return get_data(self, 'SP_DCPGetObject(%s,%s,%s)', (objectid, objectclass, objectname))

    def get_object_by_name(self, objectname):
        return get_data_pk(self, 'SP_DCPGetObject(%s,%s,%s)', (None, None, objectname))
    
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
    
    def get(self, roleid=None, name=None): # Can lookup by either roleid or name
        return get_data_pk(self, 'SP_DCPGetRole(%s,%s,%s,%s)', (roleid, None, name, None))

    def get_roles(self, roleid=None, roleclass=None, name=None, internalflag=None):
        return get_data(self, 'SP_DCPGetRole(%s,%s,%s,%s)', (roleid, to_array(roleclass), name, internalflag))
    
    def save(self, myRole):
        return save_data('SP_DCPUpsertRole', (
            myRole.roleid,
            myRole.roleclass,
            myRole.name,
            myRole.description,
            myRole.publicflag,
            myRole.schoollist,
            myRole.usertypelist,
            myRole.userlist,
            myRole.internalflag
            )
        )[0] # Return ID
    
    def delete(self, myRole):
        return delete_data('SP_DCPDeleteRole', (myRole.roleid, myRole.internalflag))

    def modify_role_item(self, myRole, userid, schoolid, usertype, changetype = 'A'):
        return save_data('SP_DCPModifyRoleItem', (myRole.roleid, userid, schoolid, usertype, changetype))

    def get_role_options(self, **kwargs):
        return generate_options(
            items = self.get_roles(**kwargs), 
            idfield = "roleid", 
            displayfield = "name"
        )

class RoleACLManager(models.Manager):
    def all(self):
        return self.get_role_acls()
    
    def get(self, roleid, objectid, objectclass):
        return get_data_pk(self, 'SP_DCPGetRoleACL(%s,%s,%s,%s)', (roleid, objectid, objectclass, None))
    
    def get_role_acls(self, roleid = None, objectid = None, objectclass = None, accesslevel = None):
        return get_data(self, 'SP_DCPGetRoleACL(%s,%s,%s,%s)', (roleid, objectid, objectclass, accesslevel))
    
    def save(self, myRoleACL, acllist=None):
        return save_data('SP_DCPUpsertRoleACL', (
            myRoleACL.roleid,
            myRoleACL.objectid,
            myRoleACL.objectclass,
            myRoleACL.accesslevel,
            to_json(acllist)
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
    roleclass = models.CharField(max_length=50, verbose_name='Clase')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    publicflag = models.BooleanField(verbose_name='General')
    schoollist = ArrayField(models.IntegerField())
    usertypelist = ArrayField(models.CharField(max_length=2))
    userlist = ArrayField(models.IntegerField())
    internalflag = models.BooleanField(verbose_name='Internal')

    objects = RoleManager()
    
    def modify_role_item(self, userid = None, schoolid = None, usertype = None, changetype = 'A'):
        return Role.objects.modify_role_item(self, userid, schoolid, usertype, changetype)

class RoleACL(Role, Object):
    
    accesslevel = models.SmallIntegerField(primary_key=True)
    
    objects = RoleACLManager()