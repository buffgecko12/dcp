import unittest
from test_setup import *
from lib.UsefulFunctions.dataUtils import * 

from wakemeup.models.environment import *
    
class testFile(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        self.myfile_db = create_file(filesource='DB') # Database
        self.myfile_gd = create_file(filesource='GD',alternatefileid='ID1234',fileattributes=to_json({'userid':10})) # Google Drive
        self.myfile_ul = create_file(filesource='UL',filename='contract-1-congrats', fileURL='https://drive.google.com/open?id=0B4E6alUgHua8Qld0d3FrMHV1TUE',contractid=1) # URL
        self.myfile_fs = create_file(filesource='FS',schoolid=1,schoolyear=2000) # File system, different school year

        self.mycategory = create_category()
    
    def testCreateFile(self):
        self.assertTrue(self.myfile_db.fileid)

    def testGetFile(self):
        self.assertTrue(File.objects.get(self.myfile_db.fileid))
        self.assertTrue(File.objects.all())
        self.assertTrue(File.objects.get_files(contractid=1))
        self.assertTrue(File.objects.get_files(schoolid=1))
        self.assertTrue(File.objects.get_files(schoolyear=2000))

        # Google drive
        self.assertTrue(File.objects.get_files(alternatefileid='ID1234'))
        self.assertTrue(File.objects.get_files(attributefilter=to_json({'userid':10})))
        self.assertFalse(File.objects.get_files(attributefilter=to_json({'userid':11})))
        
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