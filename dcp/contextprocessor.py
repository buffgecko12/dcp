# Define custom context processor to add context to all pages
from django.contrib.auth import get_user_model
from lib.UsefulFunctions.miscUtils import get_school_year

# Access via userinfo.keyname
def dcp(request):
    
    context = {}
    
    if(request.user.is_authenticated):
        myuser = get_user_model().objects.get_user(userid=request.user.userid)
        mydisplayinfo = myuser.manage_display_info(actiontype='getuserdisplayinfo')

        if(myuser):
            userinfo = {
                'reputationvaluedelta':mydisplayinfo['reputationvaluedelta'],
                'opennotificationsflag':mydisplayinfo['opennotificationsflag'],
                'profilepicturefile':mydisplayinfo['profilepicturefile'],
            }
            
            programinfo = {
                'currentschoolyear':get_school_year()
            }

            navigation = {
                'uploadfilepost': {
                    "fields": {
                        'source':'navbar',
                        'schoolyear':get_school_year(),
                        'programname':'incentive',
                        'fileclass':'CT'
                    }
                }
            }

            context.update({'userinfo':userinfo, 'programinfo':programinfo, 'navigation':navigation})
            
    return context

def get_current_path(request):
    return {
        'current_path' : request.get_full_path()
    }
