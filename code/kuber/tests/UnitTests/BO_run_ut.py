import unittest
import sys
sys.path.append('/wd/code/kuber/vm_type_selectors/BO_Matlab')
from BO_run import BO_run
sys.path.append('/wd/code/kuber')
from results_controller import results_controller
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets
sys.path.append('../../../SSOT')
from conf import ssot
from vm_trace_logger import vm_trace_logger
import pickle

class BO_run_ut(unittest.TestCase):
    def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
        ssot.services = ['s1','s2','s3']        

    # def test_meets_performance(self):
    #     res_controll = results_controller('bo','top',True,1000)
    #     testobj = BO_run(('s1','s3'),res_controll)
    #     result = testobj.meets_perf('2','gen','4')
    #     self.assertTrue(result[0],0.051)
    #     self.assertTrue(result[1],[-1, -1, -1])
    
    def test_bo_run_dump(self):
        res_controll = results_controller('bo','top',True,1000)
        testobj = BO_run(('s1','s3'),res_controll)
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'w') as f:
            pickle.dump(testobj, f)

    def test_dump_bo_run(self):
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'r') as f:
            bo_run = pickle.load(f)
        result = bo_run.meets_perf('2','gen','4')
        self.assertTrue(result[0],0.051)
        self.assertTrue(result[1],[-1, -1, -1]) 
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'w') as f:
            pickle.dump(bo_run, f)
    def test_propagation(self):
        res_controll = results_controller('bo','top',True,1000)
        testobj = BO_run(('s1','s3'),res_controll)
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'w') as f:
            pickle.dump(testobj, f)
        
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'r') as f:
            bo_run = pickle.load(f)
        result = bo_run.meets_perf('2','gen','4')
        self.assertTrue(result[0],0.051)
        self.assertTrue(result[1],[-1, -1, -1]) 
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'w') as f:
            pickle.dump(bo_run, f)
        
        res_controll = bo_run.result_controller 
        testobj = BO_run(('s1',),res_controll)
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'w') as f:
            pickle.dump(testobj, f)
        
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'r') as f:
            bo_run = pickle.load(f)
        result = bo_run.meets_perf('2','gen','4')
        self.assertTrue(result[0],0.051)
        self.assertTrue(result[1],[-1, -1, -1])
        

        


if __name__ == '__main__':
    unittest.main()
