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
                'file':{'objectclass':'BO','objectname':'file'},
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

            roles = Role.objects.get_roles()

            # Update roles
            for role in roles:
                if role.name == "File - Edit":
                    
                    # Update name
                    role.name = "File - Create"
                    role.save()

                    # Remove teacher from role (perform after saving role info)
                    role.modify_role_item(usertype='TR', changetype='D')
                    
                elif role.name == "Program - View":
                    role.name = "General - View"
                    role.save()

                elif role.name == "Program - Edit":
                    role.name = "General - Edit"
                    role.save()

                elif role.name == "Program - Delete":
                    role.name = "General - Delete"
                    role.save()

        elif myversion == '2.0.2':

            # New Objects
            objectlist = {
                'gallery_projects':{'objectclass':'BO','objectname':'gallery_projects'},
                'gallery_photos':{'objectclass':'BO','objectname':'gallery_photos'}
            }
            
            # New roles
            rolelist = {

                # Gallery Projects
                'role_get_gallery_projects':{'roleclass':'OT','name':'Gallery Projects - View','description':'Read/download access on gallery projects','publicflag':True}, 
                'role_edit_gallery_projects':{'roleclass':'OT','name':'Gallery Projects - Edit','description':'Edit access on gallery projects'},
                'role_create_gallery_projects':{'roleclass':'OT','name':'Gallery Projects - Create','description':'Create access on gallery projects','usertypelist':['SA']},
                'role_delete_gallery_projects':{'roleclass':'OT','name':'Gallery Projects - Delete','description':'Delete access on gallery projects','usertypelist':['SU']},

                # Gallery Photos
                'role_get_gallery_photos':{'roleclass':'OT','name':'Gallery Photos - View','description':'Read/download access on gallery photos','publicflag':True}, 
                'role_edit_gallery_photos':{'roleclass':'OT','name':'Gallery Photos - Edit','description':'Edit access on gallery photos'},
                'role_create_gallery_photos':{'roleclass':'OT','name':'Gallery Photos - Create','description':'Create access on gallery photos','usertypelist':['SA']},
                'role_delete_gallery_photos':{'roleclass':'OT','name':'Gallery Photos - Delete','description':'Delete access on gallery photos','usertypelist':['SU']},

            }

            # New ACLs
            acllist = {
                
                # Gallery Projects
                'role_get_gallery_projects':[{'object':'gallery_projects','accesslevel':4}],
                'role_edit_gallery_projects':[{'object':'gallery_projects','accesslevel':8}],
                'role_create_gallery_projects':[{'object':'gallery_projects','accesslevel':10}],
                'role_delete_gallery_projects':[{'object':'gallery_projects','accesslevel':12}],
                
                # Gallery Photos
                'role_get_gallery_photos':[{'object':'gallery_photos','accesslevel':4}],
                'role_edit_gallery_photos':[{'object':'gallery_photos','accesslevel':8}],
                'role_create_gallery_photos':[{'object':'gallery_photos','accesslevel':10}],
                'role_delete_gallery_photos':[{'object':'gallery_photos','accesslevel':12}],
                
            }
            
            # Add to setup list
            setup_list.append(
                setup.setup_config('authorization', objectlist=objectlist, rolelist=rolelist, acllist=acllist)
            )

    # Apply updates
    print("\n### Applying v{0} updates".format(upgradeinfo['targetversion'].get('version')))
    setup.setup(setup_list)
