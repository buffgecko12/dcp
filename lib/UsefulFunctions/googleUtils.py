import os
import sys
import io

 # Import - Useful functions
from lib.UsefulFunctions.dataUtils import get_matching_item
from lib.UsefulFunctions.miscUtils import get_app_setting
import wakemeup.models.environment as env

# Import - Google
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from urllib.error import HTTPError

class GoogleDriveManager():

    def connect(self, gd):
        return get_google_service(service=gd.service,version=gd.version, permissions=gd.permissions)

    def create_structure(self, gd, gd_structure):
        try:
            # Create top-level directory if it doesn't exist
            for parent,children in gd_structure.items():
                if isinstance(children, dict) and parent != 'metadata':
        
                    # Create parent file
                    gd_file = {
                        'gd': gd,
                        'metadata': {
                            'name': parent,
                            'parents':[children.get('metadata',{}).get('parentid',{}) or gd_structure.get('metadata',{}).get('parentid',{}) or {}], # Use generated parentid, except for case of top-level
                            'properties':[children.get('metadata',{}) or gd_structure.get('metadata',{}) or {}]
                        },
                        'directoryflag':True
                        }
        
                    # Save file and store newly generated id
                    newfileid = env.File().save(gd_file=gd_file)['gd_file']['id']
        
                    # Set parentid values for child directories
                    for mychild in children:
                        if(mychild != 'metadata'):

                            currentchild = children[mychild]
                            
                            # Create metadata key if doesn't exist
                            if(not currentchild.get('metadata')):
                                currentchild['metadata'] = {}
                                
                            # Set parentid
                            currentchild['metadata']['parentid'] = newfileid
         
                    # Call method for children
                    self.create_structure(gd, children)
            
            return 'Success'
        
        except HttpError:
            print('Fail - Error creating "' + str(parent) + '"' + str(sys.exc_info()[0]) + ")")
            return 'Fail'

    def get_file(self, gd, fileid, fields):
        
        try:
            return gd.connection.files().get(fileId=fileid,fields=fields).execute()
        
        except (HttpError) as error:
            
            message = "Error: "
            status = error.resp.status
            
            if(status == 404):
                message += "File not found"
            else:
                message += error
            
            message +=  " ({})" .format(fileid)
            
            print(message)

    # Create directory / file
    def create_file(self, gd, metadata, file_data, mimetype, fields, directoryflag, file_path=None, *args, **kwargs):
    
        # Set file attributes
        if(directoryflag):
            metadata['mimeType'] = 'application/vnd.google-apps.folder'
            media_content = None
        else:
            media_content = get_gd_media_file(file=file_data, mimetype=mimetype,file_path=file_path)
        
        return gd.connection.files().create(
            body=metadata,
            media_body = media_content,
            fields=fields
        ).execute()

    def download_file(self, gd, fileid):

        request = gd.connection.files().get_media(fileId=fileid)
        stream = io.BytesIO()
        downloader = MediaIoBaseDownload(stream, request)
        done = False
        
        # Retry if we received HttpError
        try:
            for retry in range(0, 5):
                try:
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                        
                    return stream.getvalue()
                
                except (HTTPError) as error:
                    print('There was an API error: {}. Try # {} failed.'.format(error.response,retry))
                    
        except(HttpError) as error:
            print('There was an API error: {}' .format(error))
    
    def update_file(self, gd, fileid, metadata):
        try:
            return gd.connection.files().update(fileId=fileid, body=metadata).execute()
        
        except(HttpError) as error:
            print('There was an API error: {}' .format(error))

    def delete_file(self, gd, fileid, repositoryflag, permanentflag):

        # Delete / recycle file
        if(not permanentflag):
            return gd.update_file(fileid=fileid,metadata={'trashed':True})
        else:
            return gd.connection.files().delete(fileId=fileid).execute()
        
        # Delete from repository also
        if(repositoryflag):
            env.File(alternatefileid=fileid,filesource='GD').delete()

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
    
    def create_file(self, 
                    metadata, 
                    file_data = None, 
                    mimetype = 'application/octet-stream', 
                    fields = ('name,fileExtension,size,mimeType,description,id,properties'), 
                    directoryflag = False, 
                    file_path = None, 
                    *args, **kwargs):
        return self.objects.create_file(self, metadata, file_data, mimetype, fields, directoryflag, file_path)

    def get_file(self, fileid, fields=None):
        return self.objects.get_file(self, fileid, fields)

    def download_file(self, fileid):
        return self.objects.download_file(self, fileid)

    def update_file(self, fileid, metadata):
        return self.objects.update_file(self, fileid, metadata)

    def delete_file(self, fileid, repositoryflag=False, permanentflag=False):
        return self.objects.delete_file(self, fileid, repositoryflag, permanentflag)

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

def get_gd_media_file(file, mimetype, file_path=None, chunksize = (5*1024*1024), resumable=True):
    
    # Prepare file from path
    if(file_path):
        return MediaFileUpload(file_path, mimetype, chunksize, resumable)
    
    # Prepare file from binary
    else:
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