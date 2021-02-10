# Updates must be done in correct order within each version: 1) school, 2) googledrive, 3) program, 4) user, ...
import setup

from user.models.authorization import Role, Object

def upgrade(upgradeinfo):
    versionslist = (version.get('version') for version in upgradeinfo.get('upgradeversionslist'))

    # Create setup list    
    for myversion in versionslist:
        setup_list = []

        # Check version list
        if myversion == '2.0.1':
            
            # New Objects
            objectlist = {
                'program':{'objectclass':'BO','objectname':'program'},
                'file':{'objectclass':'BO','objectname':'file', 'objectid':getattr(Object.objects.get_object_by_name('file'), 'objectid')}, # Included to make installer work below
            }
            
            # New roles
            rolelist = {

                # Progam
                'role_get_program':{'roleclass':'PG','name':'Program - View','description':'Read/download access on program info','usertypelist':['TR']},
                'role_edit_program':{'roleclass':'PG','name':'Program - Edit','description':'Edit access on program info'},
                'role_create_program':{'roleclass':'PG','name':'Program - Create','description':'Create access on program info','usertypelist':['SA']},
                'role_delete_program':{'roleclass':'PG','name':'Program - Delete','description':'Delete access on program info','usertypelist':['SU']},

                # Buyer                
                'role_buyer':{'roleclass':'US','name':'Buyer','description':'Comprador','usertypelist':['BR']},
            }

            # New ACLs
            acllist = {
                
                # Program
                'role_get_program':[{'object':'program','accesslevel':4}],
                'role_edit_program':[{'object':'program','accesslevel':8}],
                'role_create_program':[{'object':'program','accesslevel':10}],
                'role_delete_program':[{'object':'program','accesslevel':12}],
                
                # Buyer
                'role_buyer':[{'object':'file','accesslevel':10}], # (upload files)
            }
            
            # Add to setup list
            setup_list.append(
                setup.setup_config('authorization', objectlist=objectlist, rolelist=rolelist, acllist=acllist)
            )

            # Remove "teacher" usertype from role
            filecreaterole = Role.objects.get(name='File - Edit') # New name is File - Create
            filecreaterole.modify_role_item(usertype='TR', changetype='D')

        elif myversion == '2.0.2':
            pass

    # Apply updates
    print("\n### Aplying v{0} updates".format(upgradeinfo['targetversion'].get('version')))
    setup.setup(setup_list)
