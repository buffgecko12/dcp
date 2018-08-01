# Define custom context processor to add context to all pages
from django.contrib.auth import get_user_model

# Access via userinfo.keyname
def userinfo(request):
    if(request.user.is_authenticated):
        myuser = get_user_model().objects.get_user(userid=request.user.userid)
        mydisplayinfo = myuser.manage_display_info(actiontype='getuserdisplayinfo')

        if(myuser):
            return {
                "userinfo": {
                    'reputationvaluedelta':mydisplayinfo['reputationvaluedelta'],
                    'opennotificationsflag':mydisplayinfo['opennotificationsflag'],
                    'profilepicturefile':mydisplayinfo['profilepicturefile'],
                }
            }        
            
    return {}

def get_current_path(request):
    return {
        'current_path' : request.get_full_path()
        }