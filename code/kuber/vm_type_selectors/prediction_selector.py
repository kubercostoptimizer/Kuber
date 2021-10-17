import sys
import logging
sys.path.append('../SSOT')
from conf import ssot
import copy
import prediction

"""
Purpose: selects a VM type for a service combination using binary search
Interface: run(combination,results_cache)
""" 
class Prediction_selector:
        def __init__(self):
             self.vm_types = ssot.get_vm_types()
            
        """
        Purpose: run for the combination with previous data in self.results_controller
        Input  : current combination and existing results cache 
        Output : least cost VM type that satisfies performance target
        """    
        def run(self, combination, results_controller):
            # try:
            self.results_controller = results_controller 
            if len(combination) == 1: #already collected for training
                return self.results_controller.get_best_vm(combination)
            return self.results_controller.get_best_predicted_VM(combination)
            # except Exception as e:
            #     logging.error(e)
                
        
Prediction_selector = Prediction_selector()