import sys
import logging
sys.path.append('../SSOT')
from conf import ssot
import copy
import random

"""
Purpose: selects a VM type for a service combination using binary search
Interface: run(combination,results_cache)
""" 
class Random:
        def __init__(self):
             self.vm_types = copy.deepcopy(ssot.get_vm_types())
            
        """
        Purpose: run for the combination with previous data in results_cache
        Input  : current combination and existing results cache 
        Output : least cost VM type that satisfies performance target
        """    
        def run(self, combination, results_controller):
            self.results_controller = results_controller
            self.vm_types = self.results_controller.tobe_executed_vm_types(combination) # select from the VM types that are not yet executed
       

            while len(self.vm_types) > 0:
                random_index = random.randrange(0,len(self.vm_types))
                current_vm_type = self.vm_types[random_index] # randomly select the next VM type to execute
                current_best = ssot.get_vm(self.results_controller.get_best_vm(combination)) # best so far
                if current_best is None or current_best['price'] > current_vm_type['price']:
                    logging.info('---------------------------- '+str(current_vm_type['name'])+' -------------------------------------') 
                    # randomly selected vm type is better than current best
               
                    result = self.results_controller.get_result(combination,current_vm_type)
                    
                    if result == None or not result: # not we can't determine result or its false
                        logging.info('result is '+str(result))
                        del self.vm_types[random_index] # move to next VM type
                    else:
                        # print combination,current_vm_type['name']
                        logging.info('[Random] Got best VM type '+str(current_vm_type['name']))
                        break # exit
                    logging.info('-------------------------------------------------------------------')
                elif current_best is not None:
                    self.results_controller.add_experiment(False,combination,current_best,True)
                    logging.info('[Random] running '+str(combination) +' current best '+ str(current_best['name'])+' VM type to evaluvate '+str(current_vm_type['name']))
                    break
                else:
                    logging.error('current_vm_type is None')
                    break
            return self.results_controller.get_best_vm(combination) 
        
Random = Random()