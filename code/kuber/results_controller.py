import subprocess
import sys
sys.path.append('../../../SSOT') #for unittest
sys.path.append('../SSOT')
from conf import ssot
sys.path.append('../')
from experiment import experiment
import logging
import copy
from util import *
sys.path.append('../../search')
sys.path.append('search')
from search import GreedySearch
from search import PopulationBasedSearch
from results_cache_client import results_cache_client
import prediction

class OutOfBudget(Exception):
    pass

class EndExecution(Exception):
    pass

"""
Porpose: 
    1. It gets and stores the results obtained during kuber runs.
    2. It maintins a cache of executed experiments and uses it to propagated results.
    3. Keeps track of bookkeeping required to evaluvate approches.

Iterface:
    1. get_result(combination, vm_type) -> True/False or None
    2. get_best_vm(combination) -> best VM type
"""
class results_controller:
    def __init__(self,vm_type_selector,mode,enable_propagation,max_buget,simulate=False):
        # service combination -> vm -> service -> api -> performance
        self.experiments_cache = {}   # cache contains all experiments performed
        self.propagated_experiments = {}
        self.predicted_experiments = {}
        self.predicted_experiments_cache = {}

        self.propagation_enabled = enable_propagation
        
        self.results_cache = dict()
        self.total_number_experiments = 0
        self.experiment_cost = 0
        self.exp_index_per_sc = {}
        self.budget = max_buget
        self.mode = mode
        self.vm_type_selector = vm_type_selector
        self.current_deployment = None
        self.current_best_deployment = None
        self.current_best_deployment_price = 100000000
        self.init_predict = False
        # if true works with only data we have with out executing any new experiments
        self.dry_run = simulate
        self.experiment = experiment
        self.num_WID_runs = 0
        self.add_trace = True

    def init_prediction(self):
        self.predictor = prediction.prediction(self)
        self.init_predict = True
    
    def predict_meets_target(self,combination,vm_name,ref_vm1,ref_vm2,results):
        from targets import performance_targets

         # Get all the predicted VMs
        #logging.info('[Results Controller Prediction] analysing prediction results for combination '+str(combination)+' and vm type '+str(vm_name))

        if vm_name in results.keys():
            for service in results[vm_name].keys():
                for api in results[vm_name][service].keys():
                        target = performance_targets.get_performance_target_in_execution_time(service,api)
                        if target == 0:
                            continue
                        logging.info('[Results Controller Prediction] '+str(vm_name)+' '+str(service)+' '+str(api)+' perf: '+str(results[vm_name][service][api])+' target: '+str(target))
                        if results[vm_name][service][api] > target:
                            logging.info('[Results Controller Prediction] returning false')
                            return False
        else:
            logging.info('[Results Controller Prediction] returning none')
            return None
        logging.info('[Results Controller Prediction] returning true')
        return True

    def get_best_predicted_VM(self,combination,ref_vm1=None,ref_vm2=None):
        if self.init_predict:
            logging.info('[Results Controller Prediction] predicting for: '+str(combination))
            
            if ref_vm1 is None or ref_vm2 is None:
                vm_types = self.tobe_executed_vm_types(combination)

                if len(vm_types) == 0:
                    logging.info('[Results Controller Prediction] None of the VMs work')
                    return None
                logging.info('reference VM type 1 '+str(vm_types[0]['name']))
                logging.info('reference VM type 2 '+str(vm_types[len(vm_types)/2]['name']))

                ref_vm1 = vm_types[0]['name']
                ref_vm2 = vm_types[len(vm_types)/2]['name']
                # logging.info('[Results Controller Prediction] Reference VM type A: '+str(ref_vm1))
                # logging.info('[Results Controller Prediction] Reference VM type B: '+str(ref_vm2))

            logging.info('[Results Controller Prediction] getting prediction results for '+str(combination))
            if self.get_result(combination,ssot.get_vm(ref_vm1)):
                return ref_vm1

            results = self.predictor.get_predictions(combination,ref_vm1,ref_vm2)

            for vm_name in ssot.get_vm_names():
                logging.warning('VM type: '+str(vm_name)+' result: '+str(self.predict_meets_target(combination,vm_name,ref_vm1,ref_vm2,results)))

            best_working_VM_type = None

            # Find the least cost VM
            for vm_name in ssot.get_vm_names():
                
                meets_perf = self.predict_meets_target(combination,vm_name,ref_vm1,ref_vm2,results)
                
                if meets_perf is None:
                    continue
                elif meets_perf and best_working_VM_type is None :
                    # check if the actual experiment will work
                    if self.get_result(combination,ssot.get_vm(vm_name)):     
                        # if yes, then we found our match
                        logging.info('[Results Controller Prediction] found best VM type: '+str(vm_name))
                        self.predicted_experiments[combination] = vm_name
                        best_working_VM_type = vm_name
                    else:
                        logging.info('[Results Controller Prediction] executed due to bad prediction, VM type: '+str(vm_name))
                elif not meets_perf:
                        # store these values somewhere
                        logging.info('[Results Controller Prediction] propagating predicted values for VM type: '+str(vm_name))

                        if combination not in self.predicted_experiments_cache.keys():
                            self.predicted_experiments_cache[combination] = {}
                        if vm_name not in self.predicted_experiments_cache[combination].keys(): # can't execute more than once
                            # update cache
                            self.predicted_experiments_cache[combination][vm_name] = Experiment_run(combination, vm_name, meets_perf)
                            self.predicted_experiments_cache[combination][vm_name].index = -1

            return best_working_VM_type
                    
    def get_exper_data(self,vm_name, combination):
        results = {}
        meets_perf = True
        from targets import performance_targets
                
        for service in combination: 
            # Get performance and create different fingerprints for different APIs
            for api in performance_targets.get_apis_in_a_service(service):
                target = performance_targets.get_performance_target(service,api)

                if target != 0:
                    logging.debug('[Results Controller Prediction] getting data for prediction '+str(service)+' api: '+str(api))

                    if service not in results.keys():
                        results[service] = {}
                        
                    if api not in results.keys():
                        results[service][api] = {}

                    max_value = 0
                    max_index = 0

                    
                    for index in range(experiment.num_repeatitions):
                        perf = copy.deepcopy(experiment.get_execution_time(index, vm_name , combination, service, api,self.dry_run))
                        if perf is None:
                            logging.warning('Data for service: '+str(service)+' api: '+str(api)+' not present')
                            continue
                        perf = round(perf,4)
                        if perf > max_value:
                            max_value = perf
                            max_index = index
                        
                        worked = self.experiment.meets_performance_for_index(index,combination,vm_name)

                        if not worked:
                            meets_perf = False
                            break
                    metrics = copy.deepcopy(experiment.get_metrics(max_index, vm_name, combination))
                    results[service][api] = (max_value,metrics)
        return results

    def init_tracer(self):
        from vm_trace_logger import vm_trace_logger
        self.tracer = vm_trace_logger
        self.tracer.init(self.vm_type_selector,self.mode,self.budget,self,ssot.get_services()) 
        if not self.dry_run:
            self.tracer.is_write_mode = True
        else:
            self.tracer.is_write_mode = False
    

    def get_executed_experiments(self,combination):
        if combination in self.experiments_cache.keys():
                return self.experiments_cache[combination]
        else:
                return {}
    
    def get_propagated_experiments(self,combination):
        if combination in self.propagated_experiments.keys():
                return self.propagated_experiments[combination]
        else:
                return {}

    """
    Purpose: find related combination works
    Input  : current combination, relevant combination,and vm type
    Output : True -> if all APIs meets performance targets, else False
    None can be returned when both combinations have ntg in common
    or if relevant_combination is never executed on the VM type
    """ 
    def is_relevant_combination_works(self,current_combination,relevant_combination,vm_type):
            experiments = self.experiments_cache[relevant_combination]
            if vm_type['name'] in experiments.keys(): # relevant combination already executed the VM type
                logging.debug('is relevant combination works')
                return experiment.relevant_meets_perf(current_combination,relevant_combination,vm_type['name'])
            else:
                return None # if the experiment is not executed yet
            return None
    """
    Purpose: check if atleast one superset satisfies performance targets
    Input  : current combination and vm type
    Output : True -> if all APIs meets performance targets
    We will return False in two cases:
    1. when superset doesn't work.
    2. no relevent combination exists that got executed on vm type
    So don't use false to mean superset doesn't work
    """ 
    def does_superset_works(self,current_combination,vm_type):
            for relevant_combination, experiments in self.experiments_cache.items():
                if set(current_combination).issubset(set(relevant_combination)) and current_combination != relevant_combination:
                        meets_perf = self.is_relevant_combination_works(current_combination,relevant_combination,vm_type)
                        #logging.debug('[results controller] current: '+str(current_combination)+' relevant: '+str(relevant_combination)+' '+str(vm_type['name'])+' '+str(meets_perf))
                        if meets_perf == None:
                            continue
                        if meets_perf and self.propagation_enabled:
                            self.add_experiment(False,current_combination,vm_type,True)
                            return True # atleast one superset works
            return False # not even one superset works
    
    
    def does_predicted_subset_works(self,current_combination,vm_name):
            for relevant_combination, experiments in self.predicted_experiments_cache.items():
                if set(relevant_combination).issubset(set(current_combination)):
                        #logging.info('[results controller] current: '+str(current_combination)+' relevant: '+str(relevant_combination))
                        if vm_name in experiments.keys():
                            meets_perf = experiments[vm_name].meets_perf
                            #logging.info('[results controller] current: '+str(current_combination)+' relevant: '+str(relevant_combination)+' '+str(vm_name)+' '+str(meets_perf))
                            if meets_perf == None:
                                continue
                            if not meets_perf:
                                self.add_experiment(False,current_combination,ssot.get_vm(vm_name),False)
                                return False # atleast one subset doen't works
            return True # all subsets works 


    """
    Purpose: check if all known subset satisfies performance
    Input  : current combination and vm typee
    Output : False -> if some APIs doesn't meet performance targets
    We will return True in two cases:
    1. when subset does work.
    2. no relevent combination exists that got executed on vm type
    So don't use true to mean subset does work
    """ 
    def does_subset_works(self,current_combination,vm_type):
                for relevant_combination, experiments in self.experiments_cache.items():
                    if set(relevant_combination).issubset(set(current_combination)):
                            meets_perf = self.is_relevant_combination_works(current_combination,relevant_combination,vm_type)
                            #logging.debug('[results controller] current: '+str(current_combination)+' relevant: '+str(relevant_combination)+' '+str(vm_type['name'])+' '+str(meets_perf))
                            if meets_perf == None:
                                continue
                            if not meets_perf:
                                if self.propagation_enabled:
                                    self.add_experiment(False,current_combination,vm_type,False)
                                return False # atleast one subset doen't works
                return True # all subsets works 

    def known_vm_types(self,combination):
         all_vm_types = copy.deepcopy(ssot.get_vm_types())
         executed_vm_types = []
         for vm_type in all_vm_types:
              if self.propagation_enabled and not self.does_subset_works(combination,vm_type):
                  executed_vm_types.append(vm_type)
         return executed_vm_types

    def tobe_executed_vm_types(self, combination):
            all_vm_types = copy.deepcopy(ssot.get_vm_types())
            executed_vm_types = []
            for vm_type in all_vm_types:
                #logging.debug('testing '+str(vm_type['name'])+' for combination '+str(combination)+' does subset works '+str(self.does_subset_works(combination,vm_type)))
                #logging.info(str(combination)+' '+str(vm_type['name'])+' '+str(self.does_predicted_subset_works(combination,vm_type)))
                if not experiment.is_complete_exper_data_exists(combination,vm_type) and (not self.propagation_enabled or self.does_subset_works(combination,vm_type)): 
                    if self.vm_type_selector != 'Prediction_selector' or self.does_predicted_subset_works(combination,vm_type['name']):
                        #logging.info('added the VM type '+str(vm_type['name']))
                        executed_vm_types.append(vm_type)
            return executed_vm_types

 
    def has_ran(self,combination,vm_type):
        if combination in self.experiments_cache.keys():
            if vm_type['name'] in self.experiments_cache[combination].keys():
                return True
        subsets_works = self.does_subset_works(combination,vm_type)
        supersets_works = self.does_superset_works(combination,vm_type)
        if subsets_works == False or supersets_works == True: # decidable
            return True

        return False

    """
    Purpose: get best VM type for the combination from all the data we have on it
    Input  : current combination 
    Output : least cost VM type that satisfies performance target
    """  
    def get_best_vm(self,combination):

        if self.vm_type_selector == 'Prediction_selector':
            if combination in self.predicted_experiments.keys():
                return self.predicted_experiments[combination]

        # best VM type on executed experiments
        best_exe_vmname = self.get_best_exe_vmtype(combination)
        best_prop_vmname = self.get_best_propagated_vmtype(combination)
        
        if best_exe_vmname == None and best_prop_vmname == None:
            #logging.info('[Results Controller] getting best VM '+str(combination)+' None')
            return None
        elif best_exe_vmname == None:
            #logging.info('[Results Controller] getting best VM '+str(combination)+' '+str(best_exe_vmname))
            return best_prop_vmname
        elif best_prop_vmname == None:
            #logging.info('[Results Controller] getting best VM '+str(combination)+' '+str(best_prop_vmname))
            return best_exe_vmname
        elif ssot.get_vm_cost(best_exe_vmname) <= ssot.get_vm_cost(best_prop_vmname):
            #logging.info('[Results Controller] getting best VM '+str(combination)+' '+str(best_exe_vmname))
            return best_exe_vmname
        elif ssot.get_vm_cost(best_exe_vmname) > ssot.get_vm_cost(best_prop_vmname):
            #logging.info('[Results Controller] getting best VM '+str(combination)+' '+str(best_prop_vmname)) 
            return best_prop_vmname

    def get_best_exe_vmtype(self,combination):

        if combination not in self.experiments_cache.keys():
             return None
        executed_experiments = self.experiments_cache[combination]

        experiments_meet_perf = list(filter((lambda experiment: experiment.meets_perf), executed_experiments.values()))
        sort = sorted(experiments_meet_perf, key=lambda experiment: copy.deepcopy(ssot.get_vm_cost(experiment.vm_type)))
        if len(sort) == 0:
            return None
        return sort[0].vm_type
    
    def get_best_propagated_vmtype(self, combination):
        if self.propagation_enabled:
            vm_types = copy.deepcopy(ssot.get_vm_types()) # list is already sorted
            for vm_type in vm_types:
                if combination in self.propagated_experiments.keys() and vm_type['name'] in self.propagated_experiments[combination].keys():
                    if self.propagated_experiments[combination][vm_type['name']]:
                        return vm_type['name']
                # if self.does_superset_works(combination,vm_type):
                #     return vm_type['name']

    """
    Purpose: Book keeping for executed and propagated experiments
    Input  : Type of experiment, combination, VM_type, and result
    Output : Updates internal cache and count variables
    """ 
    def add_experiment(self,executed,combination,vm_type,meets_perf):
            from vm_trace_logger import vm_trace_logger
            self.init_tracer()
            #logging.info('Executed '+str(executed)+' prop enabled '+str(self.propagation_enabled)+' add trace '+str(self.add_trace))

            if not executed and not self.propagation_enabled:
                # experiment is propagated while propagation is not enabled
                # ignore
                return
            elif not executed and self.propagation_enabled:
                # Propagated values
                if combination not in self.propagated_experiments.keys():
                    self.propagated_experiments[combination] = {} 
                self.propagated_experiments[combination][vm_type['name']] = meets_perf
                if self.add_trace:
                    vm_trace_logger.add_trace(False,combination,vm_type,meets_perf)
            elif executed:
                # Executed values   
                # init caches
                if combination not in self.exp_index_per_sc.keys():
                    self.exp_index_per_sc[combination] = 0
                if combination not in self.experiments_cache.keys():
                    self.experiments_cache[combination] = {}
                if vm_type['name'] not in self.experiments_cache[combination].keys(): # can't execute more than once
                    # update cache
                    self.exp_index_per_sc[combination] = self.exp_index_per_sc[combination] + 1
                    self.experiments_cache[combination][vm_type['name']] = Experiment_run(combination, vm_type['name'], meets_perf)
                    self.experiments_cache[combination][vm_type['name']].index = self.exp_index_per_sc[combination]
                    #logging.info('logging data')
                    # book keeping
                    self.total_number_experiments = self.total_number_experiments + 1
                    self.experiment_cost = self.experiment_cost + vm_type['price']
                    self.budget = self.budget - vm_type['price']
                    logging.info('Combination: '+str(combination)+' vm: '+str(vm_type['name']))
                    logging.warning('Budget decreased: '+str(self.budget))
                    if self.add_trace:
                        vm_trace_logger.add_trace(True,combination,vm_type,meets_perf)

    def get_propagated_result(self,combination,vm_type):
            # Try to infer the result with existing data
            subsets_works = self.does_subset_works(combination,vm_type)
            if self.vm_type_selector =='Prediction_selector' and subsets_works:
                subsets_works = self.does_predicted_subset_works(combination,vm_type['name'])
                if not subsets_works:
                    logging.info('[Results Controller] propagating predicted value as false')
            supersets_works = self.does_superset_works(combination,vm_type)
            if subsets_works == False: # if any of the subsets doesn't work
                logging.info('[Results Controller] propagating false on '+str(vm_type['name']))
                is_executed = False 
                return False
            elif supersets_works == True: # if any of the supersets doesn't work
                logging.info('[Results Controller] propagating true on  '+str(vm_type['name']))
                is_executed = False
                return True
            else:
                logging.info('[Results Controller] can not propagate with existing data')
                return None
    
    """
    Purpose: 
        1. gets whether combination meets targets on VM type
        2. It returns from results cache if we have enough data to infer
        3. else it will execute using profiler
    Input  : Combination and VM_type
    Output : True -> if all APIs meets performance targets, else False
    It returns None when budget is up
    """ 
    def get_result(self, combination, vm_type):
        logging.info('[Results Controller] Getting result for '+str(combination)+' on '+vm_type['name'])
        meets_perf = None 
        is_executed = None
        if self.propagation_enabled:
            meets_perf = self.get_propagated_result(combination,vm_type)
            logging.info("propagated "+str(meets_perf))
            if meets_perf is not None:
                logging.info('[Results Controller] determined result from propagation on '+vm_type['name'])
                is_executed = False


        if is_executed == None: # can't decide with current information so execute experiment
            if self.budget <= 0:
                raise OutOfBudget
            is_executed = True

            if not self.propagation_enabled:
                meets_perf = self.get_propagated_result(combination,vm_type)
                logging.info("propagated "+str(meets_perf))

            if meets_perf is None:
                logging.info('[Results Controller] reading existing results')
                meets_perf = results_cache_client.get_result(combination,vm_type)
            
            if meets_perf is None:
                logging.info('[Results Controller] Executing on '+vm_type['name'])
                meets_perf = experiment.meets_performance(combination, vm_type['name'],self.dry_run)
            else:
                logging.info('[Results Controller] getting result from existing base on '+vm_type['name'])
            logging.warning(str(combination))
            self.add_experiment(is_executed,combination,vm_type,meets_perf)

        
        return meets_perf

