import unittest
import sys
sys.path.append('../../../SSOT')
from conf import ssot 
sys.path.append('../../vm_type_selectors')
from Kuber_O import Kuber_O
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets
sys.path.append('../../')
import results_controller
from vm_trace_logger import vm_trace_logger
sys.path.append('../../../Tools')
from logconf import logconf

class Kuber_O_ut(unittest.TestCase):
    def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
        vm_trace_logger.is_write_mode = False
    
    def test_get_future_combinations_level1(self):
         # The get future combinations function gives all future combinations that needs to passed to WID to assume everything else is working
         Kuber_O.services = ['s1','s2','s3','s4']
         # We want all combinations of (s2,s3,s4) 
         fcombinations = Kuber_O.get_future_combinations(('s1',))

         # fcombinations should be a list of following combinations
         # (s2,), (s3), (s4)
         # (s2,s3), (s3,s4), (s2,s4)
         # (s2,s3,s4) 
         self.assertItemsEqual(fcombinations, [('s2',),('s3',),('s4',),('s2','s3'),('s3','s4'),('s2','s4'),('s2','s3','s4')])

    def test_get_future_combinations_level2(self):
         # The get future combinations function gives all future combinations that needs to passed to WID to assume everything else is working
         Kuber_O.services = ['s1','s2','s3','s4']
         # We want all combinations of (s2,s3,s4) 
         fcombinations = Kuber_O.get_future_combinations(('s1','s2'))

         # fcombinations should be a list of following combinations
         # (s3,s4) 
         self.assertItemsEqual(fcombinations, [('s3','s4')])

    def test_get_future_combinations_level3(self):
         # The get future combinations function gives all future combinations that needs to passed to WID to assume everything else is working
         Kuber_O.services = ['s1','s2','s3','s4']
         # We want all combinations of (s2,s3,s4) 
         fcombinations = Kuber_O.get_future_combinations(('s1','s2','s3'))

         # fcombinations should be a list of following combinations
         # empty set
         self.assertItemsEqual(fcombinations, [])

    def test_get_future_combinations_level4(self):
         # The get future combinations function gives all future combinations that needs to passed to WID to assume everything else is working
         Kuber_O.services = ['s1','s2','s3','s4']
         # We want all combinations of (s2,s3,s4) 
         fcombinations = Kuber_O.get_future_combinations(('s1','s2','s3','s4'))

         # fcombinations should be a list of following combinations
         # empty list
         self.assertItemsEqual(fcombinations, [])

    def test_WID_inputs_level1A(self):
          # This function should get all combinations -> best VM types for already executed experiments
          # It also gets all future combinations that are not explored.
          self.maxDiff = None
          Kuber_O.services = ['s1','s2','s3','s4']
          results_cache = {}
          results_cache[('s1',)] = ssot.get_vm('a1.medium')
          results_cache[('s2',)] = ssot.get_vm('a1.medium')
          results_cache[('s3',)] = ssot.get_vm('a1.medium')
          results_cont = results_controller.results_controller('Kuber_O','bottom',False, 100)
          results_cont.results_cache = results_cache
          results_cache = Kuber_O.WID_inputs(('s4',),results_cont)
          expected_results_cache = {('s1',) :  ssot.get_vm('a1.medium'), ('s2',) : ssot.get_vm('a1.medium'), ('s3',) : ssot.get_vm('a1.medium'), ('s2','s3') : ssot.get_vm('a1.medium'),('s1','s3') : ssot.get_vm('a1.medium'),('s1','s2') : ssot.get_vm('a1.medium'),('s1','s2','s3') : ssot.get_vm('a1.medium')}
          self.assertDictEqual(expected_results_cache, results_cache)
     
    def test_WID_inputs_level1B(self):
          # This function should get all combinations -> best VM types for already executed experiments
          # It also gets all future combinations that are not explored.
          self.maxDiff = None
          Kuber_O.services = ['s1','s2','s3','s4']
          results_cache = {}
          results_cache[('s1',)] = ssot.get_vm('a1.large')
          results_cache[('s2',)] = ssot.get_vm('a1.medium')
          results_cache[('s3',)] = ssot.get_vm('a1.medium')
          results_cont = results_controller.results_controller('Kuber_O','bottom',False, 100)
          results_cont.results_cache = results_cache
          results_cache = Kuber_O.WID_inputs(('s4',),results_cont)
          expected_results_cache = {('s1',) : ssot.get_vm('a1.large'), \
                                    ('s2',) : ssot.get_vm('a1.medium'), \
                                    ('s3',) : ssot.get_vm('a1.medium'), \
                                    ('s2','s3') : ssot.get_vm('a1.medium'),\
                                    ('s1','s3') : ssot.get_vm('a1.large'),\
                                    ('s1','s2') : ssot.get_vm('a1.large'),\
                                    ('s1','s2','s3') : ssot.get_vm('a1.large')
                                    }
          self.assertDictEqual(expected_results_cache, results_cache)

    def test_WID_inputs_level2A(self):
          # This function should get all combinations -> best VM types for already executed experiments
          # It also gets all future combinations that are not explored.
          self.maxDiff = None
          Kuber_O.services = ['s1','s2','s3','s4']
          results_cache = {}
          results_cache[('s1',)] = ssot.get_vm('a1.medium')
          results_cache[('s2',)] = ssot.get_vm('a1.medium')
          results_cache[('s3',)] = ssot.get_vm('a1.medium')
          results_cache[('s4',)] = ssot.get_vm('a1.medium')
          results_cache[('s1','s2')] = ssot.get_vm('a1.large')
          results_cache[('s1','s3')] = ssot.get_vm('a1.large')
          results_cache[('s1','s4')] = ssot.get_vm('a1.large')
          results_cache[('s2','s3')] = ssot.get_vm('a1.large')
          results_cache[('s2','s4')] = ssot.get_vm('a1.large')
          results_cont = results_controller.results_controller('Kuber_O','bottom',False, 100)
          results_cont.results_cache = results_cache
          results_cache = Kuber_O.WID_inputs(('s4',),results_cont)
          expected_results_cache = {('s1',) :  ssot.get_vm('a1.medium'), \
                                    ('s2',) : ssot.get_vm('a1.medium'), \
                                    ('s3',) : ssot.get_vm('a1.medium'), \
                                    ('s4',) : ssot.get_vm('a1.medium'), \
                                    ('s1','s2') : ssot.get_vm('a1.large'), \
                                    ('s1','s3') : ssot.get_vm('a1.large'), \
                                    ('s1','s4') : ssot.get_vm('a1.large'), \
                                    ('s2','s3') : ssot.get_vm('a1.large'), \
                                    ('s2','s4') : ssot.get_vm('a1.large'), \
                                    ('s1','s2','s3') : ssot.get_vm('a1.large')
                                    }
          self.assertDictEqual(expected_results_cache, results_cache)



if __name__ == '__main__':
    unittest.main()