import sys
sys.path.append('search')
from search import GreedySearch
from search import PopulationBasedSearch
sys.path.append('../SSOT')
from conf import ssot
from experiment import experiment
import results_controller
import logging

def optimistic_solution(budget,simulate):
    tried_combinations = {}
    results_cache = {}
    services = ssot.get_services()
    current_level = len(services)
    vm_types = ssot.get_vm_types()
    experiments = results_controller.results_controller('Optimistic','mixed',True, budget,simulate)
    
    # Cheapest solution: putting all services in cheapest VM
    current_combination = ssot.get_service_combinations_at_level(current_level)
    cheapest_vm = vm_types[0]

    # updates the results_cache for the combination
    for comb in current_combination:     #<- this should match what comes out of WID
        results_cache[tuple(sorted(comb))] = cheapest_vm
    current_solution = PopulationBasedSearch(services,results_cache).solve()

    num_WID_calls = 1

    while experiments.budget > 0: # run until budget is over

        # check if the current solution works
        final_result = True
        logging.warning('[Optimistic solution] Solution cost: '+str(current_solution[1]))
        for node in current_solution[0]:
            logging.warning('[Optimistic solution] executing combination '+str(node.combination)+' VM '+str(node.vm_type['name']))
            result = experiments.get_result(tuple(sorted(node.combination)),node.vm_type)
            result = False
            if result is None or not result:
                final_result = False
                results_cache[tuple(sorted(node.combination))] = ssot.get_next_cheapest_vm(node.vm_type['name']) # <- results cache should have the key for the combination but not present

        # if works its the cheapest solution
        if final_result:
            return current_solution,num_WID_calls,experiments.total_number_experiments,experiments.experiment_cost

        # if not update results cache
        for node in current_solution[0]:
            for combination in ssot.get_immediate_children_for_combination(tuple(node.combination)):
                if combination is not ():
                    #print combination # <- it should have children but showing it has none
                    if combination not in results_cache.keys():
                        results_cache[tuple(sorted(combination))] = vm_types[0]

        # get next best solution
        current_solution = PopulationBasedSearch(services,results_cache).solve()
        num_WID_calls = num_WID_calls + 1



