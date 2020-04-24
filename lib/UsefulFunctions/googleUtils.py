import os
import sys
import io
import copy
from urllib.error import HTTPError

# Import - Google
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

 # Import - Useful functions
from lib.UsefulFunctions.dataUtils import get_matching_item, to_json
from lib.UsefulFunctions.miscUtils import get_app_setting
from wakemeup import models

class GoogleService(object):

    connection = None

    def __init__(self, service='drive', version='v3', permissions=['read'], autoconnect=True, *args, **kwargs):
        super(GoogleService, self).__init__()

        self.service = service
        self.version = version
        self.permissions = permissions

        # Connect automatically
        if autoconnect:
            self.connect()

    def connect(self):
        self.connection = get_google_service(service=self.service, version=self.version, permissions=self.permissions)

class GoogleCalendar(GoogleService):

    def __init__(self, service='calendar', version='v3', calendarid='primary', *args, **kwargs):
    
        super(GoogleCalendar, self).__init__(service, version, *args, **kwargs)
    
        self.calendarid = calendarid

    def get_events(self):
        events = self.connection.events().list(calendarId=self.calendarid).execute()
        return events.get('items', [])
    
    def create_calendar(self, title, **kwargs): # available fields: description
        calendar = {'summary':title, **kwargs}
        self.connection.calendars().insert(body=calendar)

    def get_calendar(self, calendarid='primary'):
        self.connection.calendars().get(calendarId=calendarid)

class GoogleDrive(GoogleService):

    def __init__(self, service='drive', version='v3', *args, **kwargs):
        super(GoogleDrive, self).__init__(service, version, *args, **kwargs)

    def create_structure(self, gd_structure):
        
        try:
            newfile = None

            # Create top-level directory if it doesn't exist
            for parent, children in gd_structure.items():
                if isinstance(children, dict) and parent != 'metadata':
        
                    # Create parent file
                    gd_file = {
                        'gd': self,
                        'metadata': {
                            'name': parent,
                            'parents':[children.get('metadata', {}).get('parentid') or {}],
                            'properties':[children.get('metadata') or {}]
                        },
                        'directoryflag':True
                        }

                    # Save file and store newly generated id
                    newfile = models.environment.File().save(gd_file=gd_file)

                    # Set parentid values for child directories
                    for mychild in children:
                        if mychild != 'metadata':

                            currentchild = children[mychild]

                            # Create metadata key if doesn't exist
                            if not currentchild.get('metadata'):
                                currentchild['metadata'] = {}

                            # Set parentid
                            currentchild['metadata']['parentid'] = newfile['gd_file']['id']

                    # Call method for children
                    self.create_structure(children)

            return newfile

        except HttpError:
            print('Fail - Error creating "' + str(parent) + '"' + str(sys.exc_info()[0]) + ")")
            return {'fileid':None,'gd_file':None}

    # Create directory / file
    def create_file(self, 
                    metadata, 
                    file_data = None, 
                    mimetype = 'application/octet-stream', 
                    fields = ('name,fileExtension,size,mimeType,description,id,properties,webContentLink'), 
                    directoryflag = False, 
                    file_path = None):

        # Set file attributes
        if directoryflag:
            metadata['mimeType'] = 'application/vnd.google-apps.folder'
            media_content = None
        else:
            media_content = get_gd_media_file(file=file_data, mimetype=mimetype, file_path=file_path)

        return self.connection.files().create(
            body=metadata,
            media_body=media_content,
            fields=fields
        ).execute()

    def get_file(self, fileid, fields=None):
        
        try:
            return self.connection.files().get(fileId=fileid, fields=fields).execute()

        except (HttpError) as error:

            message = "Error: "
            status = error.resp.status

            if status == 404:
                message += "File not found"
            else:
                message += error

            message +=  " ({})" .format(fileid)

            print(message)

    def get_file_weblink(self, fileid):
        return self.objects.get_file(self, fileid, fields='webContentLink')['webContentLink']

    def download_file(self, fileid):

        request = self.connection.files().get_media(fileId=fileid)
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
                    return ('There was an API error: {}. Try # {} failed.'.format(error.response, retry))

        except(HttpError) as error:
            return ('There was an API error: {}' .format(error))

    def update_file(self, fileid, metadata):
        
        try:
            return self.connection.files().update(fileId=fileid, body=metadata).execute()

        except(HttpError) as error:
            print('There was an API error: {}' .format(error))

    def delete_file(self, fileid, repositoryflag=False, permanentflag=False):
        
        myresult = None

        # Delete / recycle file
        if not permanentflag:
            myresult = self.update_file(fileid=fileid, metadata={'trashed':True})
        else:
            try:
                # Handle case where file does not exist
                myresult = self.connection.files().delete(fileId=fileid).execute()
            except:
                pass

        # Delete from repository also
        if repositoryflag:
            models.environment.File(alternatefileid=fileid, filesource='GD').delete()

        return myresult

    def lookup_fileid(self, gd_locator=None, programname=None, userid=None, fileattributes={}, **kwargs):

        # Initialize new dictionary
        newattributes = copy.deepcopy(fileattributes)

        for myvar in ('gd_locator','programname','userid'):
            if eval(myvar):
                newattributes[myvar] = str(eval(myvar)) # GD returns properties as string

        myfile = models.environment.File.objects.get_files(filesource='GD', fileattributes=to_json(newattributes), **kwargs)

        if myfile:
            return myfile[0].alternatefileid # Return alternate id for first result

    def get_gd_file(self, **kwargs):
        myfileid = self.lookup_fileid(**kwargs) # Get Google File ID

        if myfileid:
            return self.get_file(self.lookup_fileid(**kwargs))
        else:
            return None

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
        },
        {
            "service":"calendar",
            "url":"https://www.googleapis.com/auth/calendar",
            "perm_map": {
                "all": "", # Read/write access to Calendars
                "write": "", # Same as "all" - read/write
                "read": ".readonly", # Read access to Calendars
                "events": ".file", # Read/write access to Events
                "events.readonly": ".events.readonly", # Read access to Events
                "settings.readonly": ".settings.readonly", # Read access to Settings
                "addons.execute": ".addon.execute" # Run as a Calendar add-on
                }
        }
    ]

    scopes = []

    # Loop through requested permissions
    for mypermission in permissions:
        myservice = get_matching_item(service_conf,'service', service)
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
    return build(serviceName=service, version=version, credentials=credentials or get_google_credentials(service=service, permissions=permissions))

def get_gd_media_file(file, mimetype, file_path=None, chunksize = (5*1024*1024), resumable=True):

    # Prepare file from path
    if file_path:
        return MediaFileUpload(file_path, mimetype, chunksize, resumable)

    # Prepare file from binary
    else:
        return MediaIoBaseUpload(file, mimetype, chunksize, resumable)
    