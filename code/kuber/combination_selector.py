import sys
sys.path.append('../../../SSOT') #for unittest
sys.path.append('../SSOT')
from conf import ssot
import logging
import copy

"""
Purpose: selects next combination to executes
Interface: get_next_combination()
""" 
class combination_selector:
    def __init__(self,mode):
            # propagation code 
            self.mode = mode  
            if self.mode == "noprop":
                self.with_propagation = False
                self.is_top = False
            else:
                self.with_propagation = True
                self.is_top = True if mode == 'top' else False # if True get combination from top of tree
            self.service_combinations = copy.deepcopy(ssot.get_service_combinations())
            self.sc_index = 0
            logging.debug('[Combination Selector] configured in mode '+str(mode))
    
    def set_current_combination(self, service_combination):
            self.sc_index = self.service_combinations.index(service_combination) + 1

    """
    Purpose: return next combination based on the mode
    Input  : mode is initialized in constructor
    Output : next combination
    Error: None is returned when we ran out of combinations
    """ 
    def get_next_combination(self):
            combination = self.service_combinations[self.sc_index]
            logging.debug('[Combination Selector] selected '+str(combination)+' to run next')
            self.sc_index = self.sc_index + 1
            if self.sc_index >= len(self.service_combinations):
                return None

            # In mixed we need to toggle between top and bottom
            # if self.mode == 'mix':
            #     self.is_top = not self.is_top
            # if self.is_top:
            #     combination = self.service_combinations[-1]
            #     del self.service_combinations[-1]
            # else:
            #     combination = self.service_combinations[0]
            #     del self.service_combinations[0]
            return combination