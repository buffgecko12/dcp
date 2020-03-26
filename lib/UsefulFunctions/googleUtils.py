 # Import - Useful functions
import os
from lib.UsefulFunctions.dataUtils import get_matching_item
from lib.UsefulFunctions.miscUtils import get_app_setting
import wakemeup.models.environment as env

# Import - Google
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import sys

class GoogleDriveManager():

    def connect(self, gd):
        return get_google_service(service=gd.service,version=gd.version, permissions=gd.permissions)

    def create_structure(self, gd, gd_structure):
    
        try:
            # Create top-level directory if it doesn't exist
            for parent,child in gd_structure.items():
                if isinstance(child, dict):
        
                    # Create file on Google Drive
                    gd_file = {
                        'gd': gd,
                        'metadata': {
                            'name': parent,
                            'parents':[child.get('parentid',{}) or gd_structure.get('parentid',{}) or {}], # Use generated parentid, except for case of top-level
                        },
                        'directoryflag':True
                        }
        
                    # Save file and store newly generated id
                    newfileid = env.File().save(gd_file=gd_file)['gd_file']['id']
        
                    # Set parentid values for child directories
                    for mychild in child:
                        if(mychild != 'parentid'):
                            child[mychild]['parentid'] = newfileid
         
                    # Call method for children
                    self.create_structure(gd, child)
            
            return 'Success'
        
        except:
            print('Fail - Error creating "' + str(parent) + '"' + str(sys.exc_info()[0]) + ")")
            return 'Fail'

    # Create directory / file
    def create_file(self, gd, metadata, file_data, mimetype, fields, directoryflag, *args, **kwargs):
    
        # Set file attributes
        if(directoryflag):
            metadata['mimeType'] = 'application/vnd.google-apps.folder'
            media_content = None
        else:
            media_content = get_gd_media_file(file_data, mimetype=mimetype)
        
        return gd.connection.files().create(
            body=metadata,
            media_body = media_content,
            fields=fields
        ).execute()

class GoogleDrive():

    connection = None

    def __init__(self, version = 'v3', permissions = ['read'], autoconnect=True, *args, **kwargs):
        super(GoogleDrive, self).__init__(*args, **kwargs)
        
        self.service = 'drive'
        self.version = version
        self.permissions = permissions

        # Connect automatically
        if(autoconnect):
            self.connect()

    # Instances of class
    objects = GoogleDriveManager()

    def connect(self):
        self.connection = self.objects.connect(self)
        
    def create_structure(self, gd_structure):
        return self.objects.create_structure(self, gd_structure)
    
    def create_file(self, metadata, file_data=None, mimetype='application/octet-stream', fields=None, directoryflag=False):
        return self.objects.create_file(self, metadata, file_data, mimetype, fields, directoryflag)

# https://developers.google.com/drive/api/v3/about-auth
def get_google_credentials(service = 'drive', permissions = ['read']):

    service_conf = [
        # Google Drive
        {
            "service":"drive",
            "url":"https://www.googleapis.com/auth/drive",
            "perm_map": {
                "all": "",
                "write": ".file",
                "read": ".readonly",
                "list": ".metadata.readonly"
                }
        }
    ]

    scopes = []

    # Loop through requested permissions
    for mypermission in permissions:
        myservice = get_matching_item(service_conf,'service',service)
        scopes.append(myservice['url'] + myservice['perm_map'][mypermission])
    
    # Return credential (must run from same directory as .json key
    originalcwd = os.getcwd()
    os.chdir(get_app_setting('BASE_DIR')) # TO-DO: Possibly change this to point to KEYS directory
    
    credentials = service_account.Credentials.from_service_account_file(
        get_app_setting('GOOGLE_APPLICATION_CREDENTIALS'), scopes=scopes)
    
    # Revert to original cwd
    os.chdir(originalcwd)

    # Delegate control to admin Google user account
    credentials = credentials.with_subject(get_app_setting('GOOGLE_DRIVE_USER'))

    return credentials

def get_google_service(service, version, permissions = ['read'], credentials = None):
    return build(serviceName=service, version=version, credentials=credentials or get_google_credentials(service=service,permissions=permissions))

def get_gd_media_file(file, mimetype, chunksize = (5*1024*1024), resumable=True):
    return MediaIoBaseUpload(file, mimetype, chunksize, resumable)

def get_gd_filepath(user, schoolyear, pathtype = None): # TO-DO: Most likely remove this
    
    user_dir = user.schoolabbreviation or '' + ' - ' + user.firstname + str(user.userid) # i.e. RBHS - Chris12

    base_path = '/'                                         # /
    schoolyear_path = base_path + str(schoolyear) + '/'     # /2020/
    contracts_path = schoolyear_path + 'Contratos/'         # /2020/Contratos/
    user_path = contracts_path + user_dir + '/'             # /2020/Contratos/RBHS - Chris12/
    contractupload_path = user_path + "Uploads/"            # /2020/Contratos/RBHS - Chris12/Uploads/

    file_paths = {
        "base":"/",
        "schoolyear":schoolyear_path,
        "contracts":contracts_path,
        "user":user_path,
        "contractupload":contractupload_path
        }
    
    if(pathtype):
        return file_paths[pathtype]
    else:
        return file_paths
    
# get GoogleDriveId for new file uploads (contenttype, user)
def get_gd_fileid(gd_storage, request, schoolyear, pathtype = 'base'):

    path = get_gd_filepath(user=request.user, schoolyear=schoolyear, pathtype=pathtype)

    if(pathtype == 'base'):
        return 'root' # Special ID for root
    else:
        return gd_storage.files().list(pageSize=1,q="appProperties has { key='drivepath' and value='" + path + "' }",fields='files(id)').execute() # Get first match