# Define custom context processor to add context to all pages
from django.contrib.auth import get_user_model

# Access via userinfo.keyname
def userinfo(request):
    myuser = request.user
    
    if(myuser.is_authenticated):
        userid = request.user.userid
        user = get_user_model().objects.get_user(userid=userid)

        if(user):
            return {
                "userinfo": {
                    "userid": user.userid,
                    "username": user.username,
                    "userdisplayname": user.firstname + ' ' + user.lastname,
                    "userrole": user.userrole,
                    "usertype": user.usertype,
                    "emailaddress": user.emailaddress,
                    "phonenumber": user.phonenumber,
                    "is_admin": user.is_admin(),
                    "is_superuser": user.is_superuser()
                }
            }        
    else:
        return {}

def get_current_path(request):
    return {
        'current_path' : request.get_full_path()
        }