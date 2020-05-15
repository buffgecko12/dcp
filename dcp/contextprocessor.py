# Define custom context processor to add context to all pages
from lib.UsefulFunctions.miscUtils import get_school_year

# Access via userinfo.keyname
def dcp(request):
    
    context = {}
    
    if(request.user.is_authenticated):
        mydisplayinfo = request.user.manage_display_info(actiontype='getuserdisplayinfo')

        # User info for UI
        userinfo = {
            'reputationvaluedelta':mydisplayinfo['reputationvaluedelta'],
            'opennotificationsflag':mydisplayinfo['opennotificationsflag'],
            'profilepicturefile':mydisplayinfo['profilepicturefile'],
        }

        # Program info        
        programinfo = {
            'currentschoolyear':get_school_year()
        }

        # Auth / permissions info
        auth = request.user.get_site_auth()

        # Navigation-specific
        navigation = {
            'link_post': {
                'upload_file': {
                    "fields": {
                        'source':'navbar',
                        'schoolyear':get_school_year(),
                        'programname':'incentive',
                        'fileclass':'contractfile'
                    }
                }
            }
        }

        # Update context
        context.update({
            'userinfo':userinfo, 
            'programinfo':programinfo, 
            'navigation':navigation, 
            'auth':auth
        })
            
    return context

def get_current_path(request):
    return {
        'current_path' : request.get_full_path()
    }
