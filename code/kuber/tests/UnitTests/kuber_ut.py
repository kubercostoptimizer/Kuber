import unittest
import sys
sys.path.append('../../')
import kuber
sys.path.append('../../')
from experiment import experiment
from targets import performance_targets
sys.path.append('../../../SSOT')
from conf import ssot

class kuber_ut(unittest.TestCase):
    def setUp(self):
        experiment.results_file_path = 'test_files/result_file.csv'
        experiment.targets_file_path = 'test_files/target_file.csv'
        performance_targets.results_file_path = 'test_files/result_file.csv'
        performance_targets.targets_file_path = 'test_files/target_file.csv'
        ssot.services = ['s1','s2','s3','s4']
    

    def test_run_sort_find_bottom(self):
        kuber_t = kuber.Kuber('sort_find','bottom',1000,False)
        deploymnet,search_cost,num_experiments = kuber_t.run()
        print deploymnet[1],search_cost,num_experiments
        for node in deploymnet[0]:
            print node.combination, node.vm_type['name']
    
    # def test_run_binary_bottom(self):
    #     kuber_t = kuber.Kuber('binary','bottom',1000,False)
    #     deploymnet,search_cost,num_experiments = kuber_t.run()
    #     print deploymnet[1],search_cost,num_experiments
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name']

    # def test_run_binary_noprop(self):
    #     kuber_t = kuber.Kuber('binary','noprop',1000,False)
    #     deploymnet,search_cost,num_experiments = kuber_t.run()
    #     print deploymnet[1],search_cost,num_experiments
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name']


    # def test_run_random_bottom(self):
    #     kuber_t = kuber.Kuber('random','bottom',1000,False)
    #     deploymnet,search_cost,num_experiments = kuber_t.run()
    #     print deploymnet[1],search_cost,num_experiments
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name']

    # def test_run_random_noprop(self):
    #     kuber_t = kuber.Kuber('random','noprop',1000,False)
    #     deploymnet,search_cost,num_experiments = kuber_t.run()
    #     print deploymnet[1],search_cost,num_experiments
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name']


    # def test_run_sort_find_noprop(self):
    #     kuber_t = kuber.Kuber('sort_find','noprop',1000,False)
    #     deploymnet,search_cost,num_experiments = kuber_t.run()
    #     print deploymnet[1],search_cost,num_experiments
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name']
    
    # def test_run_bo_top(self):
    #     deploymnet,search_cost,num_experiments = kuber.Kuber('bo','top',1000,False).run()
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name'],search_cost,num_experiments
    
    # def test_run_bo_bottom(self):
    #     deploymnet,search_cost,num_experiments = kuber.Kuber('bo','bottom',1000,False).run()
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name'],search_cost,num_experiments

    # def test_run_bo_mix(self):
    #     deploymnet,search_cost,num_experiments = kuber.Kuber('bo','mix',1000,False).run()
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name'],search_cost,num_experiments
    
    # def test_run_bo_noprop(self):
    #     deploymnet,search_cost,num_experiments = kuber.Kuber('bo','noprop',1000,False).run()
    #     for node in deploymnet[0]:
    #         print node.combination, node.vm_type['name'],search_cost,num_experiments 

if __name__ == '__main__':
    unittest.main()

