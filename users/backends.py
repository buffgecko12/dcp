from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):

        # Determine login type (e-mail vs. username)
        if '@' in str(username):
            kwargs = {'emailaddress': username}
        else:
            kwargs = {'username': username}

        # Lookup user
        user = get_user_model().objects.get_user_auth(**kwargs)
        
        # Check for valid password (if user exists)
        if (user and user.check_password(password)):
            return user
        else:
            return None
        
    def get_user(self, userid):
        return get_user_model().objects.get_user(userid=userid)