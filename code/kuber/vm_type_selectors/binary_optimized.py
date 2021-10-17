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

"""
Purpose: selects a VM type for a service combination using binary search
Interface: run(combination,results_cache)
""" 
class binary_optimized:
        def __init__(self):
             self.vm_types = ssot.get_vm_types()
             self.services = ssot.get_services()
             self.results_cache = {}
             self.num_WID_calls = 0
             self.num_skip_calls = 0
             self.skiped_VM_types = {}
        
        def does_current_dep_works(self,deployment, current_combination):
                # we need to check if all other combinations in the solution are executed already
                for node in deployment: 
                    combination = tuple(sorted(node.combination))
                    if current_combination != combination:
                        logging.info('combination '+str(combination)+' VM type '+str(node.vm_type['name']))
                        if not self.results_controller.has_ran(combination,node.vm_type): # if we have to run the experiment keep track of the count
                            self.num_skip_calls = self.num_skip_calls + 1
                        result = self.results_controller.get_result(combination,node.vm_type) # execute the experiment
                        if not result:
                            logging.warning('not working')
                            if combination in self.skiped_VM_types.keys():
                                self.results_cache[combination] = self.skiped_VM_types[combination].pop(0) # update the best VM type for the combination with next best
                            return False # We need to recompute the solution
                return True
        """
        Purpose: run for the combination with previous data in self.results_controller
        Input  : current combination and existing results cache 
        Output : least cost VM type that satisfies performance target
        """    
        def run(self, combination, results_controller):
  
            self.results_controller = results_controller 
            start_index = 0
            last_index = len(self.vm_types)-1
            best_deployment = []

            # Initialize the best deployment
            try: 
                if len(self.results_cache.keys()) != 0: # If any experiments executed already
                    best_deployment = PopulationBasedSearch(self.services,self.results_cache).solve() # find the current best deployment from them
                    self.num_WID_calls = self.num_WID_calls + 1
                    logging.info('Starting solution costs: '+str(best_deployment[1]))
            except Exception as e:
                self.num_WID_calls = self.num_WID_calls + 1
                logging.warning("Don't have a solution yet")


            try:
                while (start_index <= last_index): 
                    
                    mid =(int)(start_index+last_index)/2  # get the current middle one

                    current_vm_type = self.vm_types[mid]
                    logging.info('---------------------------- '+str(current_vm_type['name'])+' -------------------------------------')

                    if len(best_deployment) != 0: # if their is already a vaild solution

                        # Add current VM type as the best VM type for the combination and find a solution
                        current_cost = best_deployment[1]
                        results_cache_temp = copy.deepcopy(self.results_cache)
                        results_cache_temp[combination] = current_vm_type
                        cost_after_experiment = PopulationBasedSearch(self.services,results_cache_temp).solve()
                        self.num_WID_calls = self.num_WID_calls + 1
                        
                        if cost_after_experiment[1] < current_cost: # if new solution is less costly
                            
                            logging.info('Current Solution Cost: '+str(current_cost))
                            logging.info('Cost of the solution after experiment: '+str(cost_after_experiment[1]))
                            
                            result = self.results_controller.get_result(combination,current_vm_type)
                            if result:
                                # if it works then check other experiments in the deployment if not executed already
                                if not self.does_current_dep_works(cost_after_experiment[0],combination):
                                    logging.warning('going back to start')
                                    continue #try a different solution
                         
                                self.results_cache[combination] = current_vm_type # add the VM type to orignial results cache as best VM type
                                best_deployment = cost_after_experiment
                                logging.info('Best solution cost: '+str(best_deployment[1]))
                        else:
                            logging.warning('[Binary Optimized] experiment '+str(combination)+' '+str(current_vm_type['name'])+' skipped')
                            result = True # If executing this experiment doesn't decrease costs, we should go towards less costly VM types

                            # We also need to note skiped VM type for future
                            if combination not in self.results_cache.keys() or current_vm_type['price'] < self.results_cache[combination]['price']:
                                self.results_cache[combination] = current_vm_type
                            else: # If the best skipped VM type does not work, we need all skipped VM types
                                if combination not in self.skiped_VM_types.keys():
                                    self.skiped_VM_types[combination] = []
                                self.skiped_VM_types[combination].append(current_vm_type)
                                self.skiped_VM_types[combination].sort(key=lambda x: x['price'])  # top of this list should be least cost VM type

                    else:  # if their is no vaild solution
                        result = self.results_controller.get_result(combination,current_vm_type)
                        if result:
                            self.results_cache[combination] = current_vm_type
                            try:
                                best_deployment = PopulationBasedSearch(self.services,self.esults_cache).solve()
                                self.num_WID_calls = self.num_WID_calls + 1
                                logging.info('Best solution cost: '+str(best_deployment[1]))
                            except Exception as e:
                                logging.info('not found a solution yet')

                    if result == None:
                        logging.error('[Binary] Got None')
                    elif result:
                        logging.info('[Binary] worked')
                        last_index = mid-1
                    else:
                        logging.info('[Binary] didnt work')
                        start_index = mid+1
                    
                    logging.info('Number of WID calls: '+str(self.num_WID_calls))
                    logging.info('Number of skip calls: '+str(self.num_skip_calls))
                    logging.info('-------------------------------------------------------------------')
            except Exception as e:
                logging.error(e)
                
        
binary_optimized = binary_optimized()