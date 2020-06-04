# Model field names must match database column names for "Raw" queries to match fields properly
from django.db import models
from wakemeup.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.stringUtils import mychr, split_filename
from lib.UsefulFunctions.dataUtils import generate_options, to_json, to_array
import lib.UsefulFunctions.googleUtils as google
from django.contrib.postgres.fields import JSONField

import copy

class FileManager(models.Manager):
    def all(self):
        return self.get_files()

    def get(self, fileid):
        return get_data_pk(self, 'SP_DCPGetFile(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (to_array(fileid), None, None, None, None, None, None, None, None, None))

    def get_files(self, fileid=None, fileclass=None, filecategory=None, alternatefileid=None, contractid=None, schoolid=None, schoolyear=None, fileattributes=None, filesource=None, accessinfo=None, hierarchyflag=False, relativeroot=None):
        
        fileid = to_array(fileid)
        filecategory = to_array(filecategory)
        
        if not hierarchyflag:
            return get_data(self, 'SP_DCPGetFile(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (fileid, fileclass, filecategory, alternatefileid, contractid, schoolid, schoolyear, fileattributes, filesource, to_json(accessinfo)))
        else:
            return get_data(self, 'SP_DCPGetFileHierarchy(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (fileid, fileclass, filecategory, alternatefileid, contractid, schoolid, schoolyear, fileattributes, filesource, to_json(accessinfo), relativeroot))

    def get_file_alt(self, fileid, filesource='GD'):
        result = self.get_files(alternatefileid=fileid, filesource=filesource)
        
        return result[0] if result else None

    def lookup_fileid(self, gd_locator=None, programname=None, userid=None, fileattributes={}, alternatefileidflag=False, **kwargs):
        
        # Initialize new dictionary
        newattributes = copy.deepcopy(fileattributes)

        for myvar in ('gd_locator','programname','userid'):
            if eval(myvar):
                newattributes[myvar] = str(eval(myvar)) # GD returns properties as string (TO-DO: Check this)

        myfile = self.get_files(filesource='GD', fileattributes=to_json(newattributes), **kwargs)

        if myfile:
            return myfile[0].alternatefileid if alternatefileidflag else myfile[0].fileid # Return alternate id for first result

    def lookup_fileid_gd(self, **kwargs):
        return self.lookup_fileid(alternatefileidflag=True, **kwargs)

    def save(self, myFile, *args, **kwargs):

        # Extract gd_file info if it exists
        gd_file = kwargs.get('gd_file')

        # Save file to google drive first (if defined)
        if gd_file:

            # Extract google drive connection
            gd = gd_file.pop('gd')

            # Save additional properties
            gd_file['metadata'].setdefault('properties',{}).update(myFile.get_properties(altproperties=gd_file['metadata'].get('properties')))

            # Save file
            gd_file = gd.create_file(**gd_file)

            # Prepare file
            gd.prepare_gd_file(gd_file)

            # Update original File attributes
            myFile.filename = gd_file.get('name')
            myFile.fileextension = gd_file.get('fileExtension')
            myFile.filesize = gd_file.get('size')
            myFile.filetype = gd_file.get('mimeType')
            myFile.filedescription = myFile.filedescription or gd_file.get('description') # Give priority to original value
            myFile.filesource = 'GD'
            myFile.alternatefileid = gd_file.get('id')
            myFile.fileattributes = to_json(gd_file['properties'])
            myFile.fileURL = myFile.fileURL or gd_file.get('webContentLink')
            myFile.schoolid = myFile.schoolid or gd_file['properties'].get('schoolid') # Give priority to original value
            myFile.schoolyear = myFile.schoolyear or gd_file['properties'].get('schoolyear') # Give priority to original value

        # Save to repository
        fileid = save_data('SP_DCPUpsertFile',
            (
                myFile.fileid,
                myFile.filename,
                myFile.fileextension,
                myFile.filesize,
                myFile.filetype,
                myFile.filedescription,
                myFile.filesource,
                myFile.filedata,
                myFile.fileURL,
                myFile.filepath,
                myFile.fileclass,
                myFile.filecategory,
                myFile.fileattributes,
                myFile.alternatefileid,
                myFile.contractid,
                myFile.schoolid,
                myFile.schoolyear
            )
         )[0]

        return {'fileid':fileid,'gd_file':gd_file}
    
    def save_batch(self, fileinfo, filesource=None, overridecustomfieldsflag=None, deleteoptions={'deleteremovedflag':False}):
        return save_data('SP_DCPUpsertFileBatch', (to_json(fileinfo), filesource, to_json(deleteoptions), overridecustomfieldsflag), returnall=True)
    
    def update_attributes(self, filelist, fileinfo, acllist):
        return save_data('SP_DCPUpdateFileAttributes', (filelist, to_json(fileinfo), to_json(acllist)))
    
    def delete(self, myFile, contractid=None, schoolid=None, alternatefileid=None, filesource=None):
        return delete_data('SP_DCPDeleteFile', (myFile.fileid, myFile.contractid, myFile.schoolid, myFile.alternatefileid, myFile.filesource))
            
class CategoryManager(models.Manager):
    def all(self):
        return self.get_categories()
    
    def get(self, categoryclass, categorytype):
        return get_data_pk(self, 'SP_DCPGetCategory(%s,%s)', (categoryclass, categorytype))
    
    def get_categories(self, categoryclass = None, categorytype = None):
        return get_data(self, 'SP_DCPGetCategory(%s,%s)', (categoryclass, categorytype))
    
    def get_category_options(self, categoryclass = None, categorytype = None):

        return generate_options(
            items = self.get_categories(categoryclass=categoryclass, categorytype=categorytype), 
            idfield = "categorytype", 
            displayfield = "categorydisplayname"
        )

class File(MyModel):
    
    fileid = models.IntegerField(primary_key=True, verbose_name='ID')
    filename = models.CharField(max_length=500, verbose_name='Archivo')
    fileextension = models.CharField(max_length=50)
    filesize = models.IntegerField()
    filetype = models.CharField(max_length=100, verbose_name='Tipo')
    filedescription = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    filesource = models.CharField(max_length=2)
    filedata = models.BinaryField()
    fileURL = models.URLField(max_length=500)
    filepath = models.CharField(max_length=256)
    fileclass = models.CharField(max_length=50)
    filecategory = models.CharField(max_length=10)
    fileattributes = JSONField()
    alternatefileid = models.IntegerField()
    contractid = models.IntegerField()
    schoolid = models.IntegerField()
    schoolyear = models.SmallIntegerField()

    # File Manager instance
    objects = FileManager()
    
    def get_properties(self, altproperties={}):
        mydict = {
            'filedescription': self.filedescription or altproperties.get('filedescription'),
            'filecategory': self.filecategory or altproperties.get('filecategory'),
            'fileclass': self.fileclass or altproperties.get('fileclass'),
            'contractid': self.contractid or altproperties.get('contractid'),
            'schoolid': self.schoolid or altproperties.get('schoolid'),
            'schoolyear': self.schoolyear or altproperties.get('schoolyear') 
        }

        for field in ('programname', 'userid', 'gd_locator'):
            myvalue = (self.fileattributes or {}).get(field)
            
            if myvalue:
                mydict[field] = myvalue
                
        return mydict
    
class Category(MyModel):
    
    categoryclass = models.CharField(max_length=50)
    categorytype = models.CharField(max_length=25)
    categorydisplayname = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    
    objects = CategoryManager()