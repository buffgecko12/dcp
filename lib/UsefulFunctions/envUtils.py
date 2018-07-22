import os

def check_devprod():
    if os.environ.get('ENV') != 'development':
        return "production"
    else:
        return "development"

def get_env_settings():
    
    myenvsettings = {}
    
    # Check what environment we're in
    myenv = check_devprod()
    
    if(myenv == "production"):\
        myenvsettings.update(
            {
                'ssl_require':True,
                'settingsmodule':'dcp.settings.prod'
                }
        )
    
    elif(myenv == "development"):
        myenvsettings.update(
            {'settingsmodule':'dcp.settings.dev'}
        )
    
    # Update dictionary
    return myenvsettings