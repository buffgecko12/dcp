# Define custom context processor to add context to all pages
from django.contrib.auth import get_user_model
from users.models import UserNotification

# Access via userinfo.keyname
def userinfo(request):
    if(request.user.is_authenticated):
        myuser = get_user_model().objects.get_user(userid=request.user.userid)

        if(myuser):
            return {
                "userinfo": {
                    'reputationvaluedelta':myuser.manage_reputation(actiontype='getdelta'),
                    'notifications':UserNotification.objects.get_notifications(userid=myuser.userid,activeonlyflag=True)
                }
            }        
            
    return {}

def get_current_path(request):
    return {
        'current_path' : request.get_full_path()
        }