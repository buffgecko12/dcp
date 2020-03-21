# Import - Useful functions
from lib.UsefulFunctions.dataUtils import get_matching_item
from lib.UsefulFunctions.miscUtils import get_app_setting

# Import - Google
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def get_google_credentials(service = 'drive', permissions = ['read']):

    service_conf = [
        # Google Drive
        {
            "service":"drive",
            "url":"https://www.googleapis.com/auth/drive",
            "perm_map": {
                "all": "",
                "read": "readonly",
                "list": "metadata"
                }
        }
    ]

    scopes = []

    # Loop through requested permissions
    for mypermission in permissions:
        myservice = get_matching_item(service_conf,'service',service)
        scopes.append(myservice['url'] + myservice['perm_map'][mypermission])
    
    # Return credential
    credentials = service_account.Credentials.from_service_account_file(
        get_app_setting('GOOGLE_APPLICATION_CREDENTIALS'), scopes=scopes)

    # Delegate control to admin Google user account
    credentials = credentials.with_subject(get_app_setting('GOOGLE_DRIVE_USER'))

    return credentials

def get_google_service(service, version, permissions = ['read'], credentials = None):
    return build(serviceName=service, version=version, credentials=credentials or get_google_credentials(service=service,permissions=permissions))

def get_google_drive(permissions = ['read']):
    return get_google_service(service='drive', version='v3', permissions=permissions)

def get_gd_media_file(file, mimetype, chunksize = (5*1024*1024), resumable=True):
    return MediaIoBaseUpload(file, mimetype, chunksize, resumable)