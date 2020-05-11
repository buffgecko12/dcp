def extended_permissions(request):
    
    permissions = {}
    
    if(request.user.is_authenticated):
        sharedaccountdisable = True if request.user.sharedaccountflag else False

        permissions.update({
                                # Navbar
                                'objects': request.user.get_object_auth(),
                                'navbar': {
                                    'contracts':{'disable':False},
                                    'files': {},
                                    'admin': {'disable': False if request.user.is_admin() else True},
                                    'reputation': {'disable': True},
                                    'notifications': {'disable': True},
                                    },
                                # My Account
                                'myaccount': {
                                    'profile': {'disable': sharedaccountdisable},
                                    'tools': {'disable': sharedaccountdisable},
                                    'reputation': {'disable': True},
                                    'badges': {'disable': True},
                                },
                            })

    return permissions
