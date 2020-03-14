# Model field names must match database column names for "Raw" queries to match fields properly
from django.db import models
from wakemeup.models.base import MyModel
from lib.UsefulFunctions.dbUtils import *
from lib.UsefulFunctions.miscUtils import *
from lib.UsefulFunctions.stringUtils import mychr
from lib.UsefulFunctions.dataUtils import generate_options

DEFAULT_SCHOOL_YEAR = get_school_year()

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
        
class FileManager(models.Manager):
    def all(self):
        return self.get_files()
    
    def get(self, fileid):
        return get_data_pk(self, 'SP_DCPGetFile(%s,%s,%s,%s,%s)', (fileid, None, None, None, None))
    
    def get_files(self, fileid = None, fileclass = None, filecategory = None, contractid = None, schoolyear = None):
        return get_data(self, 'SP_DCPGetFile(%s,%s,%s,%s,%s)', (fileid, fileclass, filecategory, contractid, schoolyear))
    
    def save(self, myFile):
        return save_data('SP_DCPUpsertFile',
            (
                myFile.fileid,
                myFile.filename,
                myFile.fileextension,
                myFile.filesize,
                myFile.filetype,
                myFile.filedescription,
                myFile.filestore,
                myFile.filedata,
                myFile.fileURL,
                myFile.filepath,
                myFile.fileclass,
                myFile.filecategory,
                myFile.contractid,
                myFile.schoolyear or DEFAULT_SCHOOL_YEAR
            )
         )[0] # Return fileid
        
    def delete(self, myFile, contractid = None):
        return delete_data('SP_DCPDeleteFile', (myFile.fileid, contractid))
            
class File(MyModel):
    
    fileid = models.IntegerField(primary_key=True, verbose_name='ID')
    filename = models.CharField(max_length=500, verbose_name='Archivo')
    fileextension = models.CharField(max_length=50)
    filesize = models.IntegerField()
    filetype = models.CharField(max_length=100, verbose_name='Tipo')
    filedescription = models.CharField(max_length=500, verbose_name='Descripci' + mychr('o') + 'n')
    filestore = models.CharField(max_length=2)
    filedata = models.BinaryField()
    fileURL = models.URLField(max_length=500)
    filepath = models.CharField(max_length=256)
    fileclass = models.CharField(max_length=50)
    filecategory = models.CharField(max_length=2)
    contractid = models.IntegerField()
    schoolyear = models.SmallIntegerField()

    # File Manager instance
    objects = FileManager()
    
class Category(MyModel):
    
    categoryclass = models.CharField(max_length=50)
    categorytype = models.CharField(max_length=10)
    categorydisplayname = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    
    objects = CategoryManager()
    