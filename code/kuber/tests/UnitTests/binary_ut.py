import unittest
import sys
sys.path.append('../../../SSOT')
from conf import ssot 
sys.path.append('../../vm_type_selectors')
from binary import binary
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets
sys.path.append('../../')
import results_controller
from vm_trace_logger import vm_trace_logger
sys.path.append('../../../Tools')
from logconf import logconf

class binary_ut(unittest.TestCase):
    def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
        vm_trace_logger.is_write_mode = False
        
    
    def test_run_a1_xlarge(self):
         #vm_trace_logger.init('top')
         results_cont = results_controller.results_controller('binary','bottom',False, 100)
         self.assertEqual(binary.run(('s1','s2'),results_cont),'t3.medium')
    
    # def test_run_M6_large(self):
    #      results_cont = results_controller.results_controller(False, 100)
    #      self.assertEqual(binary.run(('s1','s3'),results_cont)['name'],'M6.large')
    
    # def test_run_M6_xlarge(self):
    #     results_cont = results_controller.results_controller(False, 100)
    #     self.assertEqual(binary.run(('s1','s4'),results_cont)['name'],'M6.xlarge')

if __name__ == '__main__':
    unittest.main()