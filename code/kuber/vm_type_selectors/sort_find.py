import subprocess
import sys
sys.path.append('../SSOT')
from conf import ssot
import logging
import copy

class sort_find:
        def __init__(self):
           self.vm_types = copy.deepcopy(ssot.get_vm_types())
        
        def run(self,combination, results_controller):
             
             index = 0
             self.results_controller = results_controller             
             while len(self.vm_types) is not index:
                current_vm_type = self.vm_types[index]
                logging.info('---------------------------- '+str(current_vm_type['name'])+' -------------------------------------')
                result = self.results_controller.get_result(combination,current_vm_type)
                logging.info('[Sort Find] Got result '+str(result))
     
                if result is None:
                    return None
                elif result:
                    break
                index = index + 1
                logging.info('-------------------------------------------------------------------')           
             return self.results_controller.get_best_vm(combination) 

sort_find = sort_find()