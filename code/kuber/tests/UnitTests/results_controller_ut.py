import unittest
import sys
sys.path.append('../../')
import results_controller
from experiment import experiment
from targets import performance_targets
sys.path.append('../../../SSOT')
from conf import ssot

class results_controller_ut(unittest.TestCase):
    def setUp(self):
        self.test_object = results_controller.results_controller(False, 100)
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
    
    # without propagation tests
    def test_get_result_true(self):
        combination = ('s1','s2')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
    
    def test_get_result_false(self):
        combination = ('s1','s2','s4')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertFalse(self.test_object.get_result(combination,vm_type))
    
    def test_get_result_budgets(self):
        self.test_object = results_controller.results_controller(False, 0.308) # cost of M6.2xlarge
        
        # budget is enough here
        combination = ('s1','s2')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
        
        # budget is over so should return None
        combination = ('s1','s2','s4')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertEqual(self.test_object.get_result(combination,vm_type),None)

    # with propagation tests
    def test_get_result_parent_works(self):
        self.test_object = results_controller.results_controller(True, 0.308) # cost of M6.2xlarger
        
        # budget is enough here so it will run
        combination = ('s1','s2','s3')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))

         # budget is not enough here, but it works as we know about parent
        combination = ('s1','s2')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
    
    def test_get_result_child_works(self):
        self.test_object = results_controller.results_controller(True, 308) # large number
        
        # budget is not enough here, but it works as we know about parent
        combination = ('s1','s2')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
        
        # budget is enough here so it will run
        combination = ('s1','s2','s3')
        vm_type = ssot.get_vm('M6.large')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
        
    def test_get_result_child_doesnt_works(self):
        self.test_object = results_controller.results_controller(True, 0.308) # cost of M6.2xlarger
        
        # budget is enough here so it will run
        combination = ('s1','s4')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertFalse(self.test_object.get_result(combination,vm_type))

         # budget is not enough here, but it works as we know about parent
        combination = ('s1','s2','s4')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertFalse(self.test_object.get_result(combination,vm_type))
    
    def test_get_best_vm(self):
        self.test_object = results_controller.results_controller(True, 308) # large cost
        # budget is enough here
        combination = ('s1','s2')
        vm_type = ssot.get_vm('M6.2xlarge')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
        
        # budget is over so should return None
        combination = ('s1','s2','s3')
        vm_type = ssot.get_vm('M6.large')
        self.assertTrue(self.test_object.get_result(combination,vm_type))
        self.assertEqual(self.test_object.get_best_vm(('s1','s2')),ssot.get_vm('M6.large'))


if __name__ == '__main__':
    unittest.main()
