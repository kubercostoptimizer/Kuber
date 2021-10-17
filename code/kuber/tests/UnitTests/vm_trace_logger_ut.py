import unittest
import sys
sys.path.append('../../')
from vm_trace_logger import VM_tracer
import os

class VM_trace_logger_tests(unittest.TestCase):
    def setUp(self):
        self.filename = 'vm_traces.csv'
        self.test_obj = VM_tracer
        self.test_obj.init(self.filename)
    
    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
    
    #Test1: Does it create a file upon addition of a log
    def test_is_file_created(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        
        # add an entry into log
        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True)
        
        # check if file is created
        self.assertTrue(os.path.isfile(self.filename))
        os.remove(self.filename)
    
    #Test2: Does read is working fine for with propagation
    def test_is_read_works(self):
        # initialize with pre-created file containing two rows
        self.test_obj.init('test_files/vm_test_file.csv')
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)
        
        #check if its able to read all the data correctly
        self.assertEqual(num_experiments,2)
        self.assertEqual(search_cost,0.077*3)
        self.assertEqual(results_cache[('s1', 's2')]['price'],0.077)
        self.assertEqual(results_cache[('s1', 's2','s3')]['price'],0.077*2)
    
    def test_is_count_correct_noprop(self):
        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True) 
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        self.assertEqual(num_experiments,1) 
    
    def test_is_count_correct_prop(self):
        self.test_obj.add_prop_log(('s1','s3'),'M6.large',True) 
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)
        
        # we should not count propgated ones
        self.assertEqual(num_experiments,0) 
    
    def test_is_search_cost_correct_noprop(self):

        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True)
        self.test_obj.add_exe_log(('s1','s3'),'M6.large',True)  
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        self.assertEqual(search_cost,0.077*2) 
    
    def test_is_search_cost_correct_prop(self):

        self.test_obj.add_prop_log(('s1','s3'),'M6.large',True) 
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)
      
        # propgated ones doesn't cost anything
        self.assertEqual(search_cost,0) 

    
    def test_consecutive_runs_dont_affect_each_other(self):
        # First trail
        self.test_obj.init('test_files/vm_test_file.csv')
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        # check if its able to read all the data correctly
        self.assertEqual(num_experiments,2)
        self.assertEqual(search_cost,0.077*3)
        self.assertEqual(results_cache[('s1', 's2')]['price'],0.077)
        self.assertEqual(results_cache[('s1', 's2','s3')]['price'],0.077*2)

        # Second trail
        self.test_obj.init('test_files/vm_test_file.csv')
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        #check if its able to read all the data correctly
        self.assertEqual(num_experiments,2)
        self.assertEqual(search_cost,0.077*3)
        self.assertTrue(('s1', 's2') in results_cache.keys())
        self.assertTrue(('s1', 's2','s3') in results_cache.keys())
        self.assertEqual(results_cache[('s1', 's2')]['price'],0.077)
        self.assertEqual(results_cache[('s1', 's2','s3')]['price'],0.077*2)

    def test_is_file_write_works_for_true_values(self):
        
        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True)
        self.test_obj.add_exe_log(('s1','s2','s3'),'M6.xlarge',True)
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        self.assertEqual(num_experiments,2)
        self.assertEqual(search_cost,0.077*3)
        self.assertEqual(results_cache[('s1', 's2')]['price'],0.077)
        self.assertEqual(results_cache[('s1', 's2','s3')]['price'],0.077*2)
    
    def test_is_file_write_works_for_false_values(self):

        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True)
        self.test_obj.add_exe_log(('s1','s2','s3'),'M6.xlarge',False)
        self.test_obj.add_exe_log(('s1','s3'),'M6.large',False)
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(1000)

        self.assertEqual(num_experiments,3)
        self.assertEqual(search_cost,0.077*4)
        self.assertFalse(('s1','s3') in results_cache.keys())
    
    def test_budgets(self):
        self.test_obj.add_exe_log(('s1','s2'),'M6.large',True)
        self.test_obj.add_exe_log(('s1','s2','s3'),'M6.xlarge',True)
        self.test_obj.add_exe_log(('s1','s3'),'M6.large',True)
        results_cache,search_cost,num_experiments = self.test_obj.get_results_cache(0.077) 

        self.assertEqual(num_experiments,1)
        self.assertEqual(search_cost,0.077)
        self.assertEqual(results_cache[('s1', 's2')]['price'],0.077) 
        self.assertFalse(('s1','s2','s3') in results_cache.keys())
       

if __name__ == '__main__':
    unittest.main()
