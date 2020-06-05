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
from lib.UsefulFunctions.dataUtils import get_matching_item, to_json, convert_json_to_dict
from lib.UsefulFunctions.miscUtils import get_app_setting
from lib.UsefulFunctions.stringUtils import split_filename
from lib.UsefulFunctions.envUtils import check_env
from wakemeup import models

GD_FILE_FIELDS = 'name,fileExtension,size,mimeType,description,id,properties,webContentLink,iconLink,parents,shortcutDetails'

# Wrapper function to handle API errors
def google_api_safe_run(func):

    def func_wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except HttpError as error:

            try:
                errordetail = convert_json_to_dict(error.content)['error']
            except:
                errordetail = {}
            
            status = error.resp.status

            if status == 404:
                message = "Resource not found"
            else:
                message = errordetail.get('message') or error

            print("API Error: {}".format(message))
            return None

    return func_wrapper

def get_google_role(service, role):
    rolemap = {
        'drive': {
            'comment':'commenter',
            'fileorganize':'fileOrganizer',
            'organize':'organizer',
            'owner':'owner',
            'read':'reader',
            'write':'writer'
            },
        'calendar': {
            'availability':'freeBusyReader',
            'none':'none',
            'owner':'owner',
            'read':'reader',
            'write':'writer'
            }
        }
    
    return rolemap[service][role]

def get_gd_locator(gd_locator):
    myenv = check_env()
    
    if myenv == "production":
        suffix = ""
    elif myenv == "staging":
        suffix = "_stg"
    elif myenv == "test":
        suffix = "_tst"
    else:
        suffix = "_dev"

    return gd_locator + suffix

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

    defaultcalendarid = 'primary'

    def __init__(self, service='calendar', version='v3', *args, **kwargs):
        super(GoogleCalendar, self).__init__(service, version, *args, **kwargs)

    # CALENDAR
    # Creates calendar and adds it to creating user's list
    @google_api_safe_run
    def create_calendar(self, title, publicflag=False, acl=None, **kwargs):
        calendar = {'summary':title, **kwargs}
        mycalendar = self.connection.calendars().insert(body=calendar).execute()
        
        # Assign public acl
        if(publicflag):
            acl = {'scope': {'type':'default'},'role':'read'}

        if(acl):
            self.create_acl(calendarid=mycalendar['id'], **acl)
        
        return mycalendar

    # Add existing calendar to users's list
    @google_api_safe_run
    def add_calendar(self, calendarid, **kwargs):
        calendar = {'id':calendarid, **kwargs}
        return self.connection.calendarList().insert(body=calendar).execute()

    # Get base calendar data including user-fields
    @google_api_safe_run
    def get_calendar(self, calendarid=defaultcalendarid, baseflag=False):

        # Get user calendar
        if not baseflag:
            return self.connection.calendarList().get(calendarId=calendarid).execute()
        
        # Get base calendar
        else:
            return self.connection.calendars().get(calendarId=calendarid).execute()

    @google_api_safe_run
    def update_calendar(self, calendarid=defaultcalendarid, baseflag=False, **kwargs):
        
        # Update user calendar
        if not baseflag:
            return self.connection.calendarList().update(calendarId=calendarid, **kwargs).execute()
        
        # Update base calendar
        else:
            return self.connection.calendars().update(calendarId=calendarid, **kwargs).execute()

    # Get calendar's on user's calendar list
    @google_api_safe_run
    def get_calendar_list(self, **kwargs):
        return self.connection.calendarList().list(**kwargs).execute()

    # Clear all calendar events
    @google_api_safe_run
    def clear_calendar(self, calendarid):
        return self.connection.calendars().clear(calendarId=calendarid).execute()

    @google_api_safe_run
    def delete_calendar(self, calendarid, baseflag=False):
        
        # Delete calendar from user's list
        if not baseflag:
            return self.connection.calendarList().delete(calendarId=calendarid).execute()
        
        # Delete secondary calendar
        else:
            return self.connection.calendars().delete(calendarId=calendarid).execute()

    # EVENTS
    @google_api_safe_run
    def get_events(self, calendarid, starttime=None, endtime=None, orderby="startTime", **kwargs):
        events = self.connection.events().list(calendarId=calendarid, timeMin=starttime, timeMax=endtime, orderBy=orderby, singleEvents=True if orderby else None, **kwargs).execute()
        return events.get('items', [])
    
    @google_api_safe_run
    def get_event(self, calendarid, eventid, **kwargs):
        return self.connection.events().get(calendarId=calendarid, eventId=eventid, **kwargs).execute()

    @google_api_safe_run
    def create_event(self, calendarid, event, **kwargs):
        return self.connection.events().insert(calendarId=calendarid, body=event, **kwargs).execute()

    def format_event(self, starttime, endtime, description, timezone='America/Bogota', dateformat="%Y-%m-%dT%H:%M:%S%z"):
        return {
            'start':{'dateTime':starttime.strftime(dateformat),'timeZone':timezone}, 
            'end':{'dateTime':endtime.strftime(dateformat),'timeZone':timezone}, 
            'description':description
        }

    # ACLs
    @google_api_safe_run
    def create_acl(self, calendarid, scope, role='read', **kwargs):
        body = {'scope':scope, 'role':get_google_role('calendar', role)}
        return self.connection.acl().insert(calendarId=calendarid, body=body, **kwargs).execute()
    
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
                            'properties':children.get('metadata') or {}
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
                    filedata = None, 
                    fields = (GD_FILE_FIELDS), 
                    directoryflag = False, 
                    filepath = None,
                    updaterepoflag = False):

        media_content = None

        # Set file attributes
        if directoryflag:
            metadata['mimeType'] = 'application/vnd.google-apps.folder'
        elif metadata.get('mimeType') == "application/vnd.google-apps.shortcut":
            pass
        else:
            media_content = get_gd_media_file(file=filedata, mimetype='application/octet-stream', filepath=filepath)

        result = self.connection.files().create(
            body=metadata,
            media_body=media_content,
            fields=fields
        ).execute()
        
        # Update GD attributes and return file
        if updaterepoflag:
            self.sync(fileid=result['id'])
            
            # Refresh result
            result = self.get_file(fileid=result['id'])
            
        return result

    def create_shortcut(self, shortcutfilename, targetfileid, targetmimetype=None, updaterepoflag=True):
        metadata = {
            'Name': shortcutfilename,
            'mimeType': 'application/vnd.google-apps.shortcut',
            'shortcutDetails': {
                'targetId': targetfileid,
                'targetMimeType:': targetmimetype
            },
            'properties': self.get_file(fileid=targetfileid)['properties'] # Copy target file's properties
        }
        
        return self.create_file(metadata=metadata, updaterepoflag=updaterepoflag)

    @google_api_safe_run
    def export_file(self, fileid, exporttype, fields=GD_FILE_FIELDS):
        return self.connection.files().export(fileId=fileid, mimeType=exporttype, fields=fields)

    @google_api_safe_run
    def get_file(self, fileid, fields=GD_FILE_FIELDS, mediaflag=False):
        if not mediaflag:
            return self.connection.files().get(fileId=fileid, fields=fields).execute()
        else:
            return self.connection.files().get_media(fileId=fileid, fields=fields)

    @google_api_safe_run
    def get_files(self, scope="user", driveid=None, fields='files({0})'.format(GD_FILE_FIELDS), spaces="drive", paginateflag=False, ignoredirectoryflag=True, ignoretrashedflag=True, searchquery='', **kwargs):

        if ignoredirectoryflag:
            searchquery += (' and ' if searchquery else '') + "(mimeType != 'application/vnd.google-apps.folder')"

        if ignoretrashedflag:
            searchquery += (' and ' if searchquery else '') + "trashed=false"

        # Map parameters to Google API
        params = {'driveId':driveid, 'corpora':scope, 'fields':fields, 'spaces':spaces, 'q':searchquery, **kwargs}

        # Return all results at once
        if not paginateflag:
            result = []
            pagetoken = None

            while True:
                
                # Use pagetoken from previous iteration
                if pagetoken:
                    params['pageToken'] = pagetoken

                # Retrieve / store next file batch
                files = self.connection.files().list(**params).execute()
                result.extend(files['files'])
                
                pagetoken = files.get('nextPageToken')
                
                if not pagetoken:
                    break
            
            return result

        # Paginate
        else:
            return self.connection.files().list(**params)

    def get_file_weblink(self, fileid):
        return self.objects.get_file(self, fileid, fields='webContentLink')['webContentLink']

    @google_api_safe_run
    def download_file(self, fileid, mimetype=None):

        # Binary file
        if not mimetype:
            request = self.get_file(fileid=fileid, mediaflag=True)
            
        # Google Doc
        else:
            request = self.export_file(fileid=fileid, exporttype=mimetype)
            
        stream = io.BytesIO()
        downloader = MediaIoBaseDownload(stream, request)
        done = False

        # Retry if we received HTTPError
        for retry in range(0, 5):
            try:
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download %d%%." % int(status.progress() * 100))

                return stream.getvalue()

            except (HTTPError) as error:
                return ('API error: {}. Try # {} failed.'.format(error.response, retry))

    @google_api_safe_run
    def update_file(self, fileid, metadata):
        return self.connection.files().update(fileId=fileid, body=metadata).execute()

    def delete_file(self, fileid, deleteoptions={'repository':False, 'drive':False}):
        
        myresult = None

        # Delete / recycle file
        if not deleteoptions.get('drive'):
            myresult = self.update_file(fileid=fileid, metadata={'trashed':True})
        else:
            try:
                # Handle case where file does not exist
                myresult = self.connection.files().delete(fileId=fileid).execute()
            except:
                pass

        # Delete from repository also
        if deleteoptions.get('repository'):
            models.environment.File(alternatefileid=fileid, filesource='GD').delete()

        return myresult

    def get_gd_file(self, **kwargs):
        myfileid = models.environment.File.objects.lookup_fileid_gd(**kwargs) # Get Google File ID

        if myfileid:
            return self.get_file(models.environment.File.objects.lookup_fileid_gd(**kwargs))
        else:
            return None

    def prepare_gd_file(self, gd_file, actions={'updatefields':True,'setproperties':True}):

        # Update icon link        
        if actions.get('updatefields'):
            gd_file['iconLink'] = gd_file.get('iconLink','').replace("16","128") # Change to higher icon resolution
            gd_file['name'] = split_filename(gd_file.get('name'))['name'] # Parse out filename

        # Set properties (attributes) field
        if actions.get('setproperties'):
            
            shortcutinfo = gd_file.get('shortcutDetails')
            
            # Parse out shortcut info
            if shortcutinfo:
                gd_file['mimeType'] = shortcutinfo.get('targetMimeType') # Use target mimetype instead of shortcut's
                
                iconlink = gd_file['iconLink']
                index = iconlink.find("/application/")
                gd_file['iconLink'] = iconlink[:index] + "/" + shortcutinfo.get('targetMimeType') # Use target's iconlink instead of shortcut's
                
            myfile = copy.deepcopy(gd_file)

            gd_file.setdefault('properties',{}).update({
                'gd':myfile, **myfile.pop('properties', {}),
                'parentid':gd_file.get('parents',[None])[0] # Store first parent                
            })

    @google_api_safe_run
    def get_driveid(self):

        gd_write = GoogleDrive(permissions=['write'])
        
        tempfolderid = gd_write.create_file(metadata={'name':'temp'}, directoryflag=True)["id"] # Create temp folder
        rootfileid = gd_write.get_file(fileid=tempfolderid, fields='parents')["parents"][0] # Get parent ID
        gd_write.delete_file(fileid=tempfolderid) # Delete temp folder
        
        return rootfileid

    @google_api_safe_run
    def sync(self, fileid=None, deleteoptions={'deleteremovedflag':True}, ignoredirectoryflag=False, **kwargs):
        
        myfilelist = []
        mydriveid = self.get_driveid()
        
        # Get files
        if not fileid:
            myfiles = self.get_files(ignoredirectoryflag=ignoredirectoryflag, **kwargs)
        else:
            myfiles = [self.get_file(fileid=fileid)]
            deleteoptions= {'deleteremovedflag':False}

        # Don't delete top-level directory
        if not deleteoptions.get('excludefiles'):
            deleteoptions['excludefiles'] = [mydriveid]
        else:
            deleteoptions['excludefiles'].append(mydriveid)

        # Create batch file list        
        for myfile in myfiles:

            # Prep gd file
            self.prepare_gd_file(myfile)

            myproperties = myfile.get('properties', {})
            
            # Add new file to list
            myfilelist.append({
                'filename':myfile.get('name'),
                'fileextension':myfile.get('fileExtension'),
                'alternatefileid':myfile.get('id'),
                'filetype':myfile.get('mimeType'),
                'filesize':myfile.get('size'),
                'fileurl':myfile.get('webContentLink'),
                'filesource':'GD',
                'fileattributes':myproperties,
                # Remove already stored fields from properties
                'filedescription':myfile.get('description') or myproperties.pop('filedescription', None),
                'filecategory':myproperties.pop('filecategory', None),
                'contractid':myproperties.pop('contractid', None),
                'schoolid':myproperties.pop('schoolid', None),
                'schoolyear':myproperties.pop('schoolyear', None),
                'fileclass':myproperties.pop('fileclass', None)
                
            })
        
        # Call batch upsert
        result = models.environment.File.objects.save_batch(fileinfo=myfilelist, filesource='GD', deleteoptions=deleteoptions, overridecustomfieldsflag=False)
        
        return result

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
    credentials = credentials.with_subject(get_app_setting('GOOGLE_ADMIN_USER'))

    return credentials

def get_google_service(service, version, permissions = ['read'], credentials = None):
    return build(serviceName=service, version=version, credentials=credentials or get_google_credentials(service=service, permissions=permissions))

def get_gd_media_file(file, mimetype, filepath=None, chunksize = (5*1024*1024), resumable=True):

    # Prepare file from path
    if filepath:
        return MediaFileUpload(filepath, mimetype, chunksize, resumable)

    # Prepare file from binary
    else:
        return MediaIoBaseUpload(file, mimetype, chunksize, resumable)
    