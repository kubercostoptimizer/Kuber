import sys
import logging
sys.path.append('../SSOT')
from conf import ssot
import copy


"""
Purpose: selects a VM type for a service combination using binary search
Interface: run(combination,results_cache)
""" 
class binary:
        def __init__(self):
             self.vm_types = ssot.get_vm_types()
            
        """
        Purpose: run for the combination with previous data in self.results_controller
        Input  : current combination and existing results cache 
        Output : least cost VM type that satisfies performance target
        """    
        def run(self, combination, results_controller):
            try:
             self.results_controller = results_controller 
             start_index = 0
             last_index = len(self.vm_types)-1
             while (start_index <= last_index):
                
                mid =(int)(start_index+last_index)/2  # get the current middle one
    
                current_vm_type = self.vm_types[mid]
                logging.info('---------------------------- '+str(current_vm_type['name'])+' -------------------------------------')
                
                result = self.results_controller.get_result(combination,current_vm_type)
                
                if result == None:
                    logging.error('[Binary] Got None')
                    start_index = mid+1
                elif result:
                    logging.info('[Binary] worked')
                    last_index = mid-1
                else:
                    logging.info('[Binary] didnt work')
                    start_index = mid+1
                
                logging.info('-------------------------------------------------------------------')
             return self.results_controller.get_best_vm(combination)
            except Exception as e:
                logging.error(e)
                
        
binary = binary()