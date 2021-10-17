import unittest
import sys
sys.path.append('../../')
sys.path.append('../../../SSOT')
from conf import ssot
from targets import performance_targets

class performance_targets_tests(unittest.TestCase):
    def setUp(self):
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'

    # Check reading from a results file
    def test_read_service_performances(self):
        rows = performance_targets.read_service_performances()

        self.assertEqual(rows[0]['service_name'], 's1')
        self.assertEqual(rows[0]['vm_type'], 'M6.2xlarge')
        self.assertEqual(rows[0]['API_name'], 'api')
        self.assertEqual(rows[0]['performance_value(ms)'], 2)

    # Check if the number crunching is ok
    def test_calculate_performance_targets(self):
        service = 's1'
        perf_targets = performance_targets.calculate_performance_targets(service)
        self.assertEqual(perf_targets[0]['performance_target(ms)'],2)
    
    # tests the reading of targets.csv
    def test_load_performance_targets(self):
        perf_targets = performance_targets.load_performance_targets()
        self.assertEqual(perf_targets['s0']['api'],10)

    # tests the updating flow from results.csv file to targets.csv file
    def test_store_performance_targets(self):
        service = 's1'
        performance_targets.store_performance_targets(service)
        # check if the csv file has required values
        perf_targets = performance_targets.load_performance_targets()
        self.assertEqual(perf_targets['s1']['api'],2) 
    
    def test_is_performance_target_exists_positive(self):
        performance_targets.target_dict = performance_targets.load_performance_targets()
        self.assertTrue(performance_targets.is_performance_target_exists('s0'))

    def test_is_performance_target_exists_negitive(self):
        performance_targets.target_dict = performance_targets.load_performance_targets()
        self.assertFalse(performance_targets.is_performance_target_exists('s50'))
    
    def test_get_performance_target(self):
        self.assertEqual(performance_targets.get_performance_target('s1','api'),(1/2.0)*ssot.get_target_offset())

    def test_get_apis(self):
        apis = performance_targets.get_apis_in_a_service('s1')
        self.assertEqual(apis[0],'api')

if __name__ == '__main__':
    unittest.main()

