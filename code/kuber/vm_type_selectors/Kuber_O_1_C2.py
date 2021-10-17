import sys
import logging
sys.path.append('../SSOT')
from conf import ssot
import copy
sys.path.append('../../../search')
sys.path.append('../../search')
sys.path.append('search')
from search import GreedySearch
from search import PopulationBasedSearch
from itertools import combinations
import collections
import results_controller

class OrderedSet(collections.Set):
    def __init__(self, iterable=()):
        self.d = collections.OrderedDict.fromkeys(iterable)

    def __len__(self):
        return len(self.d)

    def __contains__(self, element):
        return element in self.d

    def __iter__(self):
        return iter(self.d)

"""
Purpose: selects a VM type for a service combination using sort and find while optimizing number of combinations it will run
Interface: run(combination,results_cache)
""" 
class Kuber_O_1_C2:
        def __init__(self):
             self.vm_types = ssot.get_vm_types()
             self.services = ssot.get_services()
             self.results_cache = {}
             self.num_WID_calls = 0
             self.num_skip_calls = 0
             self.skiped_VM_types = {}
        
        # Function to generate all the future combinations that can be passed to WID
        # function get_future_combinations(current_combination, services)
        # {
        #     remaining_services <- services - current_combination
	    #     future_combinations <- all subsets of remaining_services with length (>= length(current_combination) and <= length(remaining_services))
        #     return remaining_services
        # }
        def get_future_combinations(self,current_combination):
             remaining_services = OrderedSet(self.services) - OrderedSet(current_combination)
             future_combinations = list()
             for i in range(len(current_combination),len(remaining_services)+1):
                child_combinations = combinations(remaining_services,i)
                for child in child_combinations:
                    future_combinations.append(child)
             return future_combinations

        def WID_inputs_all_combinations(self,results_controller):
            
            self.results_controller.add_trace = False

            # collect existing results_cache
            results_cache = copy.deepcopy(results_controller.results_cache)

            # find best VM types, unexplored combinations can work on
            for combination in ssot.get_service_combinations():
                # check if the combination is unexplored
                if combination not in results_cache.keys():
                   # may be it does not work on any VM
                   vm_types = self.results_controller.tobe_executed_vm_types(combination)
                   if len(vm_types) != 0:
                       # it got skipped or not executed
                       results_cache[combination] = vm_types[0]                   
            return results_cache




        def WID_inputs(self,current_combination,results_controller):
            
            self.results_controller.add_trace = False
            
            # collect existing results_cache
            results_cache = copy.deepcopy(results_controller.results_cache)

            # find best VM types, unexplored combinations can work on
            for combination in self.get_future_combinations(current_combination):
                # check if the combination is unexplored
                if combination not in results_cache.keys():

                   # may be it does not work on any VM
                   vm_types = self.results_controller.tobe_executed_vm_types(combination)
                   if len(vm_types) != 0:
                       # it got skipped or not executed
                       results_cache[combination] = vm_types[0]      
            return results_cache

        def return_experiments_for_level(self,level,results_controller):
                experiments_to_vist = list()
                
                _ , current_best_price = PopulationBasedSearch(self.services, results_controller.results_cache).solve() 

                for combination in ssot.get_service_combinations_at_level(level):
                    
                    vm_index = 0
                    vm_types = copy.deepcopy(ssot.get_vm_types())
            
                    while vm_index <= len(vm_types):
                            
                            vm_type = vm_types[vm_index]
                            
                            if not results_controller.has_ran(combination,vm_type):
                                 
                                 current_experiment = (combination,vm_type)
                                 
                                 WID_inputs = self.WID_inputs(combination,results_controller) # contains unexplored combinations

                                 remaining_services = OrderedSet(self.services) - OrderedSet(combination) 

                                 future_solution, future_solution_price = PopulationBasedSearch(list(remaining_services),WID_inputs).solve() # find future solution

                                 future_solution_price = future_solution_price + vm_type['price'] # the solution produced in above step contains only services other than current combination

                                 if current_best_price > future_solution_price: # if the future solution will be cheaper
                                    experiments_to_vist.append((combination,vm_type,future_solution,future_solution_price))

                            vm_index = vm_index + 1 
                
                experiments_to_vist.sort(key= lambda x : x[3])

                return experiments_to_vist

        def run(self, combination, results_controller_t):
             
             self.results_controller = results_controller_t  

             vm_types = self.results_controller.tobe_executed_vm_types(combination)
             if len(vm_types) != 0:
                index = 0 
                while len(vm_types) is not index:
                    
                    current_vm_type = vm_types[index]
                    logging.info('---------------------------- '+str(current_vm_type['name'])+' -------------------------------------')

                    # WID_inputs = self.WID_inputs(combination,self.results_controller) # contains unexplored combinations

                    # # Check if we need to run the next VM type
                    # remaining_services = OrderedSet(self.services) - OrderedSet(combination) 
                    # future_solution, future_solution_price = PopulationBasedSearch(list(remaining_services),WID_inputs).solve() # find future solution
                    # self.results_controller.num_WID_runs = self.results_controller.num_WID_runs + 1
                    # future_solution_price = future_solution_price + current_vm_type['price']
                    
                    # current_best_price = self.results_controller.current_best_deployment_price
                    # logging.info('[Kuber_O_1_1] Cost of future solution: '+str(future_solution_price)+' current price '+str(current_best_price))
                    
                    # if current_best_price > future_solution_price:
                    self.results_controller.add_trace = True
                    result = self.results_controller.get_result(combination,current_vm_type)
                    
                    logging.info('[Kuber_O_1_C2] Got result '+str(result))
        
                    if result is None:
                        return None
                    else:
                        
                        if result:

                            # We need all the future combinations along with current combination
                            WID_inputs = self.WID_inputs_all_combinations(self.results_controller) # contains unexplored combinations
                            
                            best_future_solution, best_future_solution_price = PopulationBasedSearch(self.services,WID_inputs).solve() # find future solution
                            self.results_controller.num_WID_runs = self.results_controller.num_WID_runs + 1
                            for node in best_future_solution:
                                logging.info('Combination '+str(node.combination))
                                logging.info(node.vm_type['name'])
                                
                            self.results_controller.results_cache[combination] = ssot.get_vm(self.results_controller.get_best_vm(combination))

                            # get updated best deployment cost
                            try:
                                self.results_controller.current_best_deployment , self.results_controller.current_best_deployment_price = PopulationBasedSearch(self.services, self.results_controller.results_cache).solve()
                                self.results_controller.num_WID_runs = self.results_controller.num_WID_runs + 1
                                    
                            except Exception:
                                self.results_controller.current_best_deployment_price = 100000000
                                pass
                            
                            
                            logging.info('[Kuber_O_1_C2] Cost of updated best future solution and current solution: '+str(best_future_solution_price)+' current price '+str(self.results_controller.current_best_deployment_price))  
                            if best_future_solution_price >= self.results_controller.current_best_deployment_price:
                                logging.warning('[Kuber_O_1_1] Ending the execution !!!')
                                raise results_controller.EndExecution
                            break # move to next combination
                        # else:
                        #     logging.info('[Kuber_O_1_C2] Cost of updated best future solution and current solution: '+str(best_future_solution_price)+' current price '+str(self.results_controller.current_best_deployment_price))  
                        #     if best_future_solution_price >= self.results_controller.current_best_deployment_price:
                        #         logging.warning('[Kuber_O_1_1] Ending the execution !!!')
                        #         raise results_controller.EndExecution 
                       
                        index = index + 1
                    # else:
                    #     logging.warning('[Kuber_O_1_1] skiping the experiment')
                    #     break # if the current VM type does not improve the solution, costlier one will never be
                    logging.info('-------------------------------------------------------------------')           
             return self.results_controller.get_best_vm(combination) 
        
Kuber_O_1_C2 = Kuber_O_1_C2()