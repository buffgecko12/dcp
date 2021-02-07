# Updates must be done in correct order within each version: 1) school, 2) googledrive, 3) program, 4) user, ...
import setup

def upgrade(upgradeinfo):
    versionslist = (version.get('version') for version in upgradeinfo.get('upgradeversionslist'))

    # Create setup list    
    for myversion in versionslist:
        setup_list = []

        # Check version list
        if myversion == '2.0.1':
            
            # Object
            objectlist = {'program':{'objectclass':'BO','objectname':'program'}}
            
            # Program object - Role
            rolelist = {
                'role_get_program':{'roleclass':'PG','name':'Program - View','description':'Read/download access on program info','usertypelist':['TR']},
                'role_edit_program':{'roleclass':'PG','name':'Program - Edit','description':'Edit access on program info'},
                'role_create_program':{'roleclass':'PG','name':'Program - Create','description':'Create access on program info','usertypelist':['SA']},
                'role_delete_program':{'roleclass':'PG','name':'Program - Delete','description':'Delete access on program info','usertypelist':['SU']}
            }

            # Program object - ACL
            acllist = {
                'role_get_program':[{'object':'program','accesslevel':4}],
                'role_edit_program':[{'object':'program','accesslevel':8}],
                'role_create_program':[{'object':'program','accesslevel':10}],
                'role_delete_program':[{'object':'program','accesslevel':12}]
            }
            
            # Add to setup list
            setup_list.append(
                setup.setup_config('authorization', objectlist=objectlist, rolelist=rolelist, acllist=acllist)
            )

        elif myversion == '2.0.2':
            pass

    # Apply updates
    print("\n### Aplying v{0} updates".format(upgradeinfo['targetversion'].get('version')))
    setup.setup(setup_list)
