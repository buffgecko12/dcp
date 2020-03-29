import unittest
from test_setup import *
from test_env_setup import *
from wakemeup.models.environment import File
from googleapiclient.errors import HttpError

from UsefulFunctions.googleUtils import GoogleDrive

class testGoogleDrive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        
        # Create service connections
        cls.gd_list = GoogleDrive(permissions=['list'])
        cls.gd_read = GoogleDrive(permissions=['read'])
        cls.gd_write = GoogleDrive(permissions=['write'])

        cls.metadata = {'name': 'Test directory','parents':['root'],'properties':{'key1':'val1'}}

        cls.mymediafile = cls.gd_write.create_file(metadata={'name':'testpic.jpg'},file_path=get_abs_path('test/img/sampleimg.jpg'))
    
    def setUp(self):
        
        # Create file
        self.myfile = self.gd_write.create_file(metadata=self.metadata,directoryflag=True)
    
    def testConnection(self):
        pass
        
    def testCreateFile(self):

        # Create file (GD only)
        self.assertTrue(self.myfile['id'])

        # Create file (GD and repository)
        gd_file = {'gd': self.gd_write,'metadata': self.metadata,'directoryflag':True}
        newfile = File().save(gd_file=gd_file)

        # Store gd fileid        
        newfile_gdid = newfile['gd_file']['id']
        
        # Verify new fileids 
        self.assertTrue(newfile['fileid']) # repository
        self.assertTrue(newfile_gdid) # google drive
        
        # Delete file
        self.gd_write.delete_file(newfile_gdid)

    def testDeleteFile(self):

        myfileid = self.myfile['id']
        
        # Recycle file and verify
        self.gd_write.delete_file(fileid=myfileid)
        self.assertTrue(self.gd_write.get_file(fileid=myfileid,fields=('trashed'))['trashed'])
        
        # Permanently delete file and verify
        self.gd_write.delete_file(fileid=myfileid, permanentflag=True)
        self.assertFalse(self.gd_write.get_file(fileid=myfileid))
        
    def testCreateStructure(self):

        gd_structure = {
            'Directory 1':{
                'Sub-Directory 1a':{
                    'Sub-Directory 1b':{},
                    'metadata':{'gd_locator':'dir_1b'}
                },
                'metadata':{'gd_locator':'dir_1a'}
            },
            'metadata':{'parentid':'root','gd_locator':'dir_1'},
#             'parentid':'root' # Optional (can use value "None" or remove key entirely)
        }

        self.gd_write.create_structure(gd_structure)

        # TO-DO: Check directory created
        # Check lookup via gd_locator

    def testGetFile(self):

        # Get file
        myfile = self.gd_read.get_file(fileid=self.mymediafile['id'])
        self.assertTrue(myfile)

        # Download file        
        myfile = self.gd_read.download_file(fileid=self.mymediafile['id'])
        self.assertTrue(myfile)

    def testAuthorization(self):
        
        # Try to create file with "read" authorization
        with self.assertRaises(HttpError):
            self.gd_read.create_file(metadata=self.metadata,directoryflag=True)
        
        # Create file with "write" authorization
        self.assertTrue(self.gd_write.create_file(metadata=self.metadata,directoryflag=True)['id'])
        
    def tearDown(self):        
        self.gd_write.delete_file(fileid=self.myfile['id'])
    
    @classmethod
    def tearDownClass(cls):
        cls.mymediafile = cls.gd_write.delete_file(fileid=cls.mymediafile['id'])
    
if __name__ == '__main__':
    unittest.main() # Run all tests