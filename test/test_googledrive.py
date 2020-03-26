import unittest
from test_setup import *

from UsefulFunctions.googleUtils import GoogleDrive

class testGoogleDrive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def testConnection(self):
        
        # Connection
        gd = GoogleDrive(permissions=['write'])
        
        # Create file
        gd.create_file(metadata={'name': 'Test directory','parents':['root']},directoryflag=True,)
        
    def tearDown(self):        
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main() # Run all tests