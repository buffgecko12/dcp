# -*- coding: utf-8 -*-
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
        cls.gd_read = GoogleDrive(permissions=['read'])
        cls.gd_write = GoogleDrive(permissions=['write'])

        cls.metadata = {'name': 'Test directory', 'parents':['root'], 'properties':{'key1':'val1'}}
        cls.mymediafile = cls.gd_write.create_file(metadata={'name':'testpic.jpg'},file_path=get_abs_path('test/img/sampleimg.jpg'))

        cls.newname = 'newname'
    
    def setUp(self):
        
        # Create file
        self.myfile = self.gd_write.create_file(metadata=self.metadata, directoryflag=True)
    
    def testConnection(self):
        pass
        
    def testCreateFile(self):

        # Create file (GD only)
        self.assertTrue(self.myfile['id'])

        # Create file (GD and repository)
        gd_file = {'gd': self.gd_write, 'metadata': self.metadata, 'directoryflag':True}
        newfile = File().save(gd_file=gd_file)

        # Store gd fileid        
        newfile_gdid = newfile['gd_file']['id']
        
        # Verify new fileids 
        self.assertTrue(newfile['fileid'])  # repository
        self.assertTrue(newfile_gdid)  # google drive
        
        # Delete file
        self.gd_write.delete_file(fileid=newfile_gdid)

    def testUpdateFile(self):

        # Change file name and verify
        myfile = self.gd_write.update_file(fileid=self.myfile['id'], metadata={'name':self.newname})
        self.assertTrue(myfile['name'], self.newname)

    def testDeleteFile(self):

        myfileid = self.myfile['id']
        
        # Recycle file and verify
        self.gd_write.delete_file(fileid=myfileid)
        self.assertTrue(self.gd_write.get_file(fileid=myfileid, fields=('trashed'))['trashed'])
        
        # Permanently delete file and verify
        self.gd_write.delete_file(fileid=myfileid, deleteoptions={'repository':True, 'drive':True})
        self.assertFalse(self.gd_write.get_file(fileid=myfileid))
        
    def testCreateStructure(self):

        gd_structure = {
            'Directory 1':{
                'Sub-Directory 1a':{
                    'Sub-Directory 1b':{
                        'metadata':{'gd_locator':'dir_1b'}
                        },
                    'metadata':{'gd_locator':'dir_1a'}
                },
                'metadata':{'parentid':'root', 'gd_locator':'dir_1'},
            },
        }

        self.gd_write.create_structure(gd_structure)

        # Lookup file and verify it exists on GD
        myfileid = File.objects.lookup_fileid_gd(fileattributes={'gd_locator':'dir_1'})
        self.assertTrue(myfileid)

        # Test lookup using alternate argument
        myfileid = File.objects.lookup_fileid_gd(gd_locator='dir_1')
        self.assertTrue(myfileid)
        
        self.assertTrue(self.gd_read.get_file(fileid=myfileid))
        
        # Delete directory structure
        self.gd_write.delete_file(fileid=myfileid)

    def testGetFile(self):

        # Get file
        myfile = self.gd_read.get_file(fileid=self.mymediafile['id'])
        self.assertTrue(myfile)

        # Download file        
        myfile = self.gd_read.download_file(fileid=self.mymediafile['id'])
        self.assertTrue(myfile)

        myfiles = self.gd_read.get_files()
        self.assertTrue(myfiles)

    def testAuthorization(self):
        
        # Try to create file with "read" authorization
        with self.assertRaises(HttpError):
            self.gd_read.create_file(metadata=self.metadata, directoryflag=True)
        
        # Create file with "write" authorization
        newfile = self.gd_write.create_file(metadata=self.metadata, directoryflag=True)
        self.assertTrue(newfile['id'])
        
        # Delete file
        self.gd_write.delete_file(fileid=newfile['id'])

    def testSync(self):

        newfile = File().save(gd_file={'gd':self.gd_write,'metadata':{'name':'test_file'}, 'directoryflag':True})
        newfile_gdid = newfile['gd_file']['id']
        
        # Create sub-directories
        newfile2 = self.gd_write.create_file(metadata={'name':'Sub-directory 1', 'parents':[newfile_gdid]}, directoryflag=True)
        newfile3 = self.gd_write.create_file(metadata={'name':'Sub-directory 2', 'parents':[newfile2['id']]}, directoryflag=True)
        
        myrepofile = File.objects.get_file_alt(fileid=newfile_gdid)
        mygdfile = self.gd_read.get_file(fileid=newfile_gdid)

        # Verify file names are in sync
        self.assertEqual(myrepofile.filename, mygdfile['name'])
        
        # Change file name in GD and run sync
        myfile = self.gd_write.update_file(fileid=newfile_gdid, metadata={'name':self.newname})
        self.gd_read.sync(fileid=newfile_gdid)
        
        # Verify file names are in sync
        self.assertEqual(File.objects.get_file_alt(fileid=newfile_gdid).filename, self.gd_read.get_file(fileid=newfile_gdid)['name'])

        # Sync all files
        self.gd_read.sync()

        # Delete test file and all children
        self.gd_write.delete_file(fileid=newfile_gdid, deleteoptions={'repository':True})

    def tearDown(self):
        self.gd_write.delete_file(fileid=self.myfile['id'])
    
    @classmethod
    def tearDownClass(cls):
        cls.mymediafile = cls.gd_write.delete_file(fileid=cls.mymediafile['id'])
    
if __name__ == '__main__':
    unittest.main()  # Run all tests
