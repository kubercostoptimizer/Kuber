import unittest
import sys
sys.path.append('../../')
import kuber
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets
sys.path.append('../../../SSOT')
from conf import ssot

class targets_ut(unittest.TestCase):
      def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
        ssot.services = ['s1','s2','s3']
    
      def test_ensure_cache_is_updated(self):
          self.assertTrue(performance_targets.ensure_cache_is_updated('s1'))

if __name__ == "__main__":
    unittest.main()
     
    
