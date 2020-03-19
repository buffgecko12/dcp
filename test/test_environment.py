import unittest
from test_setup import *

from wakemeup.models.environment import *
    
class testFile(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.myfile_db = create_file(filestore='DB') # BLOB
        self.myfile_gd = create_file(filestore='GD',filename='contract-1-congrats', fileURL='https://drive.google.com/open?id=0B4E6alUgHua8Qld0d3FrMHV1TUE',contractid=1) # Google drive
        self.myfile_fs = create_file(filestore='FS',schoolid=1,schoolyear=2000) # Different school year

        self.mycategory = create_category()
    
    def testCreateFile(self):
        self.assertTrue(self.myfile_db.fileid)

    def testGetFile(self):
        self.assertTrue(File.objects.get(self.myfile_db.fileid))
        self.assertTrue(File.objects.all())
        self.assertTrue(File.objects.get_files(contractid=1))
        self.assertTrue(File.objects.get_files(schoolid=1))
        self.assertTrue(File.objects.get_files(schoolyear=2000))
        
    def testUpdateFile(self):
        self.myfile_db.filename = 'NEW NAME'
        self.myfile_db.save()
        self.myfile_db = refresh(self.myfile_db) # Refresh object
        self.assertEqual(self.myfile_db.filename, 'NEW NAME')

    def testDeleteFile(self):
        self.myfile_db.delete()
        self.assertFalse(refresh(self.myfile_db))

    def testGetCategory(self):
        self.assertTrue(Category.objects.get(categoryclass=self.mycategory.categoryclass,categorytype=self.mycategory.categorytype))
        self.assertTrue(Category.objects.all())
        self.assertTrue(Category.objects.get_categories(categoryclass=self.mycategory.categoryclass))
        self.assertTrue(Category.objects.get_category_options(categoryclass=self.mycategory.categoryclass))
        
    def tearDown(self):        
        self.myfile_db.delete()
        self.myfile_gd.delete()
        self.myfile_fs.delete()
        
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main() # Run all tests