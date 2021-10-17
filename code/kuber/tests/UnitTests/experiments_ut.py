import unittest
import sys
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets

class experiment_tests(unittest.TestCase):
    
    def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
    
    def test_load_performances(self):
        experiment.perf_dict = experiment.load_performances()
        self.assertTrue('M6.2xlarge' in experiment.perf_dict.keys())
 
    def test_meets_performance_api_true(self):
         self.assertTrue(experiment.meets_performance_api(('s1','s2','s3'),'M6.2xlarge','s3','api'))
    
    def test_meets_performance_api_false(self):
         self.assertFalse(experiment.meets_performance_api(('s1','s2','s4'),'M6.2xlarge','s4','api'))
    
    def test_meets_performance_api_zero_perf(self):
         self.assertTrue(experiment.meets_performance_api(('s1','s2','s4'),'M6.2xlarge','s1','api'))

    def test_meets_performance_api_zero_target(self):
         self.assertTrue(experiment.meets_performance_api(('s1','s2','s3'),'M6.2xlarge','s2','api'))

    def test_meets_performance_service(self):
         self.assertTrue(experiment.meets_performance_service(('s5','s6'),'M6.2xlarge','s6'))

    def test_meets_performance_service_true(self):
         self.assertTrue(experiment.relevant_meets_perf(('s1','s2'),('s1','s2','s3'),'M6.2xlarge'))

    def test_meets_performance_service_ntg_common(self):
         self.assertFalse(experiment.relevant_meets_perf(('s1','s2'),('s6','s4','s5'),'M6.2xlarge'))

    def test_meets_performance_service_bottom_up(self):
         self.assertTrue(experiment.relevant_meets_perf(('s1','s2','s3'),('s1','s2'),'M6.2xlarge'))
     
    def test_relevant_meets_perf(self):
         self.assertTrue(experiment.relevant_meets_perf(('s1','s2'),('s1','s2','s3'),'M6.2xlarge'))
    
    def test_does_service_meets_perf_true(self):
         self.assertTrue(experiment.does_service_meets_perf('s1','M6.2xlarge'))
    
    def test_does_service_meets_perf_false(self):
         self.assertFalse(experiment.does_service_meets_perf('s4','M6.2xlarge'))

    def test_does_services_meet_perf_true(self):
         self.assertTrue(experiment.does_services_meet_perf(('s1','s2','s3'),'M6.2xlarge'))
    
    def test_meets_performance_true(self):
          self.assertTrue(experiment.meets_performance(('s1','s2','s3'),'M6.2xlarge'))
    
    def test_meets_performance_false(self):
          self.assertFalse(experiment.meets_performance(('s1','s2','s4'),'M6.2xlarge'))

if __name__ == '__main__':
    unittest.main()

    