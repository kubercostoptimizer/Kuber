# Runs Bayesian Optimization on a service combination
# Input: Tuple of services e.g. ('carts','orders')
# Output: Best VM type on which it works and map of VM types on which it tried and performance data

import sys
import cPickle as pickle
import logging
import StringIO

import bo
from BO_sim import fake_bo
from BO_run import BO_run
sys.path.append('../')
from targets import performance_targets

class bointerface:
    def __init__(self):
        self.logging = logging.config.fileConfig('/wd/code/SSOT/logging.conf')
        self.numIterations = 40
        self.numInitPoints = 1
        self.stopingcondition = 1.1850e-09
        self.pathtocostfunc = '/wd/code/kuber/vm_type_selectors/BO_Matlab/cost_function.py'
        self.my_libbo = bo.initialize() # don't call twice

    def set_config(self,service_combination,results_controller):
        self.results_controller = results_controller
        self.service_combination = service_combination
        
    def run_bo(self,fake=False):
        bo_run = BO_run(self.service_combination, self.results_controller)
        logging.debug('[bointerface] dumping bo_run obj')
        with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'wb') as f:
            pickle.dump(bo_run, f)
        try:
            if fake:
                fake_bo(self.service_combination)
            else:
                logging.info('[BO] starting BO '+str(bo_run.num_constraints))
                self.my_libbo.bo(bo_run.num_constraints,self.numIterations,self.numInitPoints,self.stopingcondition,self.pathtocostfunc,nargout=0)

                logging.debug('[BO] reading results from the BO_run file') 
                with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'r') as f: # we need to update the result_controller from most recent bo_run object
                    bo_run = pickle.load(f)
                
                logging.debug('[BO] updating results') 
                self.results_controller = bo_run.result_controller

        except Exception as e:
            logging.error("didn't ran due to error "+str(e))
        
    def __del__ (self):
        self.my_libbo.terminate()
        del self.my_libbo
            
