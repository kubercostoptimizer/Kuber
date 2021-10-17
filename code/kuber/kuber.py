import subprocess
import sys
sys.path.append('../../../SSOT') #unittest
sys.path.append('../SSOT')
from conf import ssot
sys.path.append('../../search')
sys.path.append('search')
from search import GreedySearch
from search import PopulationBasedSearch
from plot import plot
sys.path.append('../')
from experiment import experiment
import math
import random
import csv
import logging
import copy
import collections

sys.path.append('../../vm_type_selectors')
sys.path.append('vm_type_selectors')
from binary import binary
import combination_selector
from vm_type_selector import vm_type_selector 
import results_controller
from vm_trace_logger import vm_trace_logger

class go_to_nextlevel(Exception):
    pass

class go_to_nextexperiment(Exception):
    pass

class Kuber:
        def __init__(self,vm_type_sel,mode,budget,simulate=True):
            logging.config.fileConfig('/wd/code/SSOT/logging.conf')
            logging.info('######################################## Kuber log ##################################')
            logging.info("VM selector: "+str(vm_type_sel))
            logging.info("Mode: "+str(mode))
            logging.info("Budget: "+str(budget))
           
            self.services = ssot.get_services()
            self.mode = mode
            self.budget = budget
            self.vm_type_sel = vm_type_sel
            self.vm_selector = vm_type_selector.get(vm_type_sel)
            self.combination_selector = combination_selector.combination_selector(mode)
            self.results_controller = results_controller.results_controller(vm_type_sel,mode,self.combination_selector.with_propagation, budget,simulate)
            self.results_cache = {}
            self.current_best_deployment = []

            self.tracer = vm_trace_logger
            self.tracer.init(vm_type_sel,mode,budget,self.results_controller,ssot.get_services()) 
          
            if not simulate:
                self.tracer.set_write_mode()
       
        def run(self):
            self.results_cache = {}
            visited_combinations = []
            
            # If trace exists read from it
            if self.tracer.trace_exists():
                 self.results_cache = self.tracer.get_results_cache(self.budget)
                 for sc in ssot.get_service_combinations_at_level(1):
                     if sc not in self.results_cache.keys():
                         self.results_cache[sc] = ssot.get_vm('M6.2xlarge')
                 self.results_controller.results_cache = self.results_cache
                 self.results_controller = self.tracer.results_controller
                 self.combination_selector.set_current_combination(self.tracer.last_combination_executed)
                 self.current_deployment, self.results_controller.current_best_deployment_price = PopulationBasedSearch(self.services,self.results_cache).solve()

            if self.vm_type_sel!='Kuber_O_2':
                if self.results_controller.budget > 0 and self.vm_type_sel=='Prediction_selector':
                    self.results_controller.init_prediction()
                    
                if self.results_controller.budget > 0:
                    
                    self.results_controller.dry_run = False
                                    
                    # Execute until all combinations visited or we run out of budget
                    while True:
                        combination = self.combination_selector.get_next_combination()  # next combination to execute
                        if combination == None: # done with all combinations exit
                            break
                        
                        logging.info('#==================================== '+str(combination)+' ====================================#')
                        try:
                            self.vm_selector.run(combination,self.results_controller) 
                            visited_combinations.append(combination)
                            self.results_controller = self.vm_selector.results_controller # for BO we need explicitly update it
                        except results_controller.OutOfBudget:
                            logging.warning('Out of budget !!!')
                            break 
                        except results_controller.EndExecution:
                            logging.warning('Their is no better solution than current one !!!')
                            break 

                        if self.results_controller.budget <= 0:
                            break
                        logging.info('======================================================================================')
                    
                    # For each combination get best VM type
                    for combination in visited_combinations:
                        best_vm_name = self.results_controller.get_best_vm(combination)
                        if best_vm_name is not None:
                            self.results_cache[combination] = ssot.get_vm(best_vm_name)
                        
                        logging.info('Best VM type found for '+str(combination)+' is '+str(best_vm_name))
                
                executed_combinations = []
                for sc_level in range(0,len(self.results_cache.keys()[-1])+1):
                    combinations = sorted(list(filter(lambda number: len(number) == sc_level+1, self.results_cache.keys())))
                    executed_combinations = executed_combinations + combinations


                #create the diagram            
                for combination in ssot.get_service_combinations():
                    if combination in executed_combinations:
                        best_vm_name =  self.results_cache[combination]
                        plot.add_sc_to_figure(combination, best_vm_name, self.results_controller.get_executed_experiments(combination), self.results_controller.get_propagated_experiments(combination))
                    else:
                        plot.add_sc_to_figure(combination, None, self.results_controller.get_executed_experiments(combination), self.results_controller.get_propagated_experiments(combination))
                    
                    if combination == executed_combinations[-1]:
                        print combination
                        break
                
                logging.warning('Number of WID runs '+str(self.results_controller.num_WID_runs))
                logging.info('######################################## Kuber end ##################################')
                return PopulationBasedSearch(self.services,self.results_cache).solve(),self.results_controller.experiment_cost,self.results_controller.total_number_experiments
            
            # elif self.vm_type_sel == 'Kuber_O_2':

            #         sys.path.append('../../vm_type_selectors')
                
            #         from Kuber_O import Kuber_O
                    
            #         for level in range(1,len(self.services)+1): # one
            #             # try:    
            #             logging.info('[Kuber O] executing on level: '+str(level))
                        
            #             # experiments in the level sorted by future prices
            #             experiments_to_execute = Kuber_O.return_experiments_for_level(level,self.results_controller)

            #             for experiment in experiments_to_execute: # two

            #                 try:
            #                     logging.info('[kuber O] executing experiment combination '+ str(experiment[0])+' on '+str(experiment[1]['name']))

            #                     # if experiment works then test remaining solution
            #                     if self.results_controller.get_result(experiment[0],experiment[1]):
                                    
                                
            #                             # future solution also works then we are done in this level
            #                             for node in experiment[2]: # three
            #                                 combination = tuple(sorted(node.combination))
            #                                 vm_type = node.vm_type
            #                                 logging.info('[kuber O] executing solution combination '+ str(combination)+' on '+str(vm_type['name']))
            #                                 if not self.results_controller.get_result(combination,vm_type):
            #                                     # remaining experiment does not work
            #                                     # so go to loop two and get next experiment
            #                                     logging.info('[Kuber O] solution does not work')
            #                                     raise go_to_nextexperiment

            #                             # experiment and solution works so go to next level (loop one)
            #                             logging.info('[Kuber O] found best solution in level: '+str(level))
            #                             raise go_to_nextlevel
            #                     else:
            #                         logging.info('[Kuber O] experiment does not work')

            #                 except go_to_nextexperiment:
            #                         logging.info('[Kuber O] moving to next experiment'
            #                         #pass
            #             # except go_to_nextlevel:
            #             #         logging.info('[Kuber O] moving to level : '+str(level))
            #             #         #pass
                    
            #         logging.info('######################################## Kuber end ##################################')
            #         return PopulationBasedSearch(self.services,self.results_cache).solve(),self.results_controller.experiment_cost,self.results_controller.total_number_experiments





        
        def store_trace_fig(self,suffix=''):
            print "Creating a Diagaram ..."
            filename = str(self.mode)+str(self.vm_type_sel)+str(self.budget)+str(suffix)
            plot.print_figure(filename)