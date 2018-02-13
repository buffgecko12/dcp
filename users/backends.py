from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):

        if '@' in str(username):
            kwargs = {'emailaddress': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get_user_auth(**kwargs)
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None
        
    def get_user(self, userid):
        try:
            return get_user_model().objects.get(userid=userid)
        except get_user_model().DoesNotExist:
            return None