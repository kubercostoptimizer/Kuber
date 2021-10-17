import sys
sys.path.append('Search')
from search import GreedySearch,PopulationBasedSearch
sys.path.append('../SSOT')
from conf import ssot
from experiment import experiment
import math
import logging
import threading

def get_best_vmtype(vm_types,service_combination,results):
        logging.config.fileConfig('../SSOT/logging.conf')
        logging.info('[sort-find] finding best VM type for '+str(service_combination))
        num_experiments = 0
        cost_experiment = 0
        print service_combination
        for vm_type in vm_types:
                num_experiments = num_experiments + 1
                cost_experiment = cost_experiment + vm_type['price']
                meets_perf =  experiment.meets_performance(service_combination, vm_type['name'])
                if meets_perf:
                    logging.info('[sort-find] best VM type for '+str(service_combination)+' '+vm_type['name'])
                    print vm_type['name']
                    results[0] = vm_type
                    results[1] = num_experiments
                    results[2] = cost_experiment
                    return

class theoretical_solution:
        def __init__(self):
            self.services = ssot.get_services()
            self.vm_types = ssot.get_vm_types()
            # sort vm types by price and first VM type that meets performance should be it.
            self.vm_types.sort(key=lambda x: x['price'])
            logging.config.fileConfig('../SSOT/logging.conf')

        def result(self):
            best_cost_per_sc_dict = dict()
            num_threads = 2
            num_experiments = 0
            cost_experiment = 0
            threads = dict()
            results = dict()
            i = 0
            for service_combination in ssot.get_service_combinations():
                 results[i] = dict()
                 threads[i] = threading.Thread(target=get_best_vmtype, args=(self.vm_types,service_combination,results[i]))
                 threads[i].start()
                 i = i+1
                 if i == num_threads:
                     i = 0
                     for j in range(num_threads):
                        threads[j].join()  
                        if results[j] != dict():
                            best_cost_per_sc_dict[service_combination] = results[j][0]
                            num_experiments = num_experiments + results[j][1]
                            cost_experiment = cost_experiment + results[j][2]
            
            if i != num_threads:
                threads[0].join()
                if results[0] != dict():
                    best_cost_per_sc_dict[service_combination] = results[0][0]
                    num_experiments = num_experiments + results[0][1]
                    cost_experiment = cost_experiment + results[0][2]

            print "==========================================="
            print "Best theoretical solution"
            print "==========================================="
            print "Total number of experiments ",num_experiments
            print "Total cost of experiments $",cost_experiment 
            # population based search uses random number based algorithm hence not deterministic
            # so for our experiments we use greedy search
            #populationSearch = PopulationBasedSearch(self.services, best_cost_per_sc_dict)
            #return populationSearch.solve()
            simpleGreedy = GreedySearch(self.services, best_cost_per_sc_dict)
            return simpleGreedy.solve()

        def get_best_vmtype(self, service_combination):
            vm_types = self.vm_types
            vm_types_meet_perf = list(filter(lambda vm: experiment.meets_performance(service_combination, vm['name']), vm_types))
            sort =  sorted(vm_types_meet_perf, key=lambda vm: vm['price'])
            if len(sort) == 0:
                return None
            return sort[0]
            
        def display_result(self):
            nodes,cost = self.result()
            print "-----------------"
            print "Population Cloud configuration and Placement:"
            print "-----------------"
            for node in nodes: 
                print str(node.combination)," deployed on ",node.vm_type['name']
            print "-----------------"
            print "Theoretical cost of deployment $",cost
            print "***************************************************************************************"
                     
theoretical_solution = theoretical_solution()
theoretical_solution.display_result()