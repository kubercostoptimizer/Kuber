import sys
import unittest
sys.path.append('../')
from opennebula_client import opennebula_client

class Opennebula_client_test(unittest.TestCase):
     def test_create_master(self):
               oc = opennebula_client()
               oc.create_master() 
               oc.add_slave('c4.large')
if __name__ == '__main__':
    unittest.main()

