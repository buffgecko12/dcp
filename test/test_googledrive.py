import unittest
from test_setup import *

from UsefulFunctions.googleUtils_new import GoogleDrive

class testGoogleDrive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
    
    def setUp(self):
        pass
    
    def testConnection(self):
        mydrive = GoogleDrive()
        mydrive.connect()
        conn = mydrive.connection
        
    def tearDown(self):        
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
if __name__ == '__main__':
    unittest.main() # Run all tests