import os

def check_env():
    myenv = os.environ.get('ENV')
    
    if myenv in('production','staging','test'):
        return myenv
    else:
        return "development"

def get_env_settings():
    
    myenvsettings = {}
    
    # Check what environment we're in
    myenv = check_env()
    
    # Production
    if(myenv == "production"):\
        myenvsettings.update(
            {
                'ssl_require':True,
                'settingsmodule':'dcp.settings.prd'
            }
        )

    # Staging    
    elif(myenv == "staging"):
        myenvsettings.update(
            {
                'ssl_require':True,
                'settingsmodule':'dcp.settings.stg'
            }
        )
    
    # Test
    elif(myenv == "test"):
        myenvsettings.update(
            {
                # 'ssl_require':True,
                'settingsmodule':'dcp.settings.tst'
            }
        )
    
    # Development
    else:
        myenvsettings.update(
            {'settingsmodule':'dcp.settings.dev'}
        )
    
    # Update dictionary
    return myenvsettings