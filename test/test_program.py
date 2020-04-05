import unittest
from test_setup import *
from lib.UsefulFunctions.dataUtils import * 

from wakemeup.models.program import Program

class testProgram(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        myprogram = Program(name='incentive program',schoolyear=2018).save()
        
    def setUp(self):
        pass
    
    def testCreateProgram(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == '__main__':
    unittest.main() # Run all tests