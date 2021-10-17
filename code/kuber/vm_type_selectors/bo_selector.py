import os.path
import logging
import sys
sys.path.append('/wd/code/kuber/vm_type_selectors/BO_Matlab')
from bointerface import bointerface as BO
sys.path.append('/wd/code/SSOT')
from conf import ssot
import pickle

class bo_t:
    def __init__(self):
        self.vm_types = ssot.get_vm_types()
        self.bo = BO()
         
    def run(self, combination, results_controller):
        self.results_controller = results_controller 
        try:
            self.bo.set_config(combination,self.results_controller)
            self.bo.run_bo()
        except Exception as e:
            logging.error(str(combination)+' has error '+str(e))

        best_vm_type = None
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'r') as f:
            shared_bo = pickle.load(f) # read BO's output
            best_vm_type = shared_bo.best_vm
            self.results_controller = shared_bo.result_controller 
            if self.results_controller.budget <= 0:
                logging.info('[BO] out of budget')
                return None 
            return self.results_controller.get_best_vm(combination)