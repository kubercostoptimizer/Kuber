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


class results_cache_client:
    def __init__(self):
        # service combination -> vm -> service -> api -> performance
        self.experiments_cache = {}   # cache contains all experiments performed
        self.results_file_path = FOLDER_CHARACTER.join([ssot.get_app_path(), '/result','Data', 'results.csv'])
        self.load_existing_data()

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
                logging.debug('[Results Cache Client] is relevant combination works')
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
                        logging.debug('[Results Cache Client] current: '+str(current_combination)+' relevant: '+str(relevant_combination)+' '+str(vm_type['name'])+' '+str(meets_perf))
                        if meets_perf == None:
                            continue
            return False # not even one superset works
    
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
                        logging.debug('[Results Cache Client] current: '+str(current_combination)+' relevant: '+str(relevant_combination)+' '+str(vm_type['name'])+' '+str(meets_perf))
                        if meets_perf == None:
                            continue
            return True # all subsets works 

    """
    Purpose: Loads performance data from self.results_file_path
    Input  : Results file path
    Output : Dict containing vm -> service_combination -> service -> api -> performance
    """
    def load_existing_data(self):
        logging.debug('[Results Cache Client] loading performance data from file '+str(self.results_file_path))
        res = {}
        line_number = 0
        with open(self.results_file_path) as results_file:
            reader = csv.DictReader(results_file)
            for row in reader:
                try:
                    line_number = line_number + 1
                    
                    # read rows from the file
                    vm = row['vm_type']
                    service_combination_tup = parse_service_combination(row['service_combination'])
                    index = int(row['index'])
                    service = row['service_name']
                    api = row['API_name']
                    performance = float(row['performance_value(ms)'])

                    # fill in the dict with vm -> service_combination -> service -> api -> performance
                    if vm not in res:
                        res[vm] = {}
                    if service_combination_tup not in res[vm]:
                        res[vm][service_combination_tup] = {} # dictionary from service combination to service
                    if index not in res[vm][service_combination_tup]:
                        res[vm][service_combination_tup][index] = {} 
                    if service not in res[vm][service_combination_tup][index]: 
                        res[vm][service_combination_tup][index][service] = {}

                    res[vm][service_combination_tup][index][service][api] = performance

                except Exception as e:
                    logging.error('[Results Cache Client] could not parse '+str(row)+' in line '+str(line_number))
                    logging.error(e)
                    pass

        for vm_name in res.keys():
            for sc in res[vm_name].keys():
                meets_perf = experiment.meets_performance(sc, vm_name, True)
                self.add_existing_experiments(sc,ssot.get_vm(vm_name),meets_perf)


    def add_existing_experiments(self,combination,vm_type,meets_perf):
            if combination not in self.experiments_cache.keys():
                self.experiments_cache[combination] = {}
            
            
            if vm_type is not None and vm_type['name'] not in self.experiments_cache[combination].keys(): # can't execute more than once
                # update cache
                self.experiments_cache[combination][vm_type['name']] = Experiment_run(combination, vm_type['name'], meets_perf)

    def get_propagated_result(self,combination,vm_type):
            # Try to infer the result with existing data
            subsets_works = self.does_subset_works(combination,vm_type)
            # if subsets_works == True:
            #     supersets_works = self.does_superset_works(combination,vm_type)

            if subsets_works == False: # if any of the subsets doesn't work
                logging.info('[Results Cache Client] propagating false on '+str(vm_type['name']))
                is_executed = False 
                return False
            # elif supersets_works == True: # if any of the supersets doesn't work
            #     logging.info('[Results Cache Client] propagating true on  '+str(vm_type['name']))
            #     is_executed = False
            #     return True
            else:
                logging.info('[Results Cache Client] can not propagate')
                return None
    
    def get_result(self, combination, vm_type):
            meets_perf = self.get_propagated_result(combination,vm_type)
            if meets_perf == None:
                meets_perf = experiment.meets_performance(combination, vm_type['name'],True)
                logging.info(meets_perf)
            return meets_perf

results_cache_client = results_cache_client()