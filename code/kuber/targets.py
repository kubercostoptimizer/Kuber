import csv
import sys
import json
import logging
from util import *
from numpy import median
sys.path.append('../../../SSOT') #for unittests
sys.path.append('../SSOT')
from conf import ssot
sys.path.append('../../../Profiler') #for unittests
sys.path.append('../Profiler')
from profiler import Profiler
from experiment import experiment

"""
Interface:
1. get_performance_target(service,api)
2. get_performance_targets(service_combination)
3. get_apis_in_a_service(service) 
"""
class performance_targets:
    
    BASE_FOLDER = '../../code'  
    FOLDER_CHARACTER = '/'  

    def __init__(self):
          
          self.targets_file_path = experiment.FOLDER_CHARACTER.join([ssot.get_app_path(), 'result','Data', 'performance_targets.csv'])
          self.results_file_path = experiment.FOLDER_CHARACTER.join([ssot.get_app_path(), 'result','Data', 'results.csv'])

          # service -> api -> performance target
          self.target_dict = self.load_performance_targets()
          self.target_offset = ssot.get_target_offset()
          self.reference_VM_type = 'M6.2xlarge'
    
    #****************************************************
    # Purpose: Uses experiments interface to execute the service combination on a reference VM type
    # Inputs:  Service combination for which performance target is needed
    # Returns: Writes the results.csv file
    #**************************************************** 
    def execute_experiments_for_performance_targets(self,service):
        logging.debug('[targets] Executing service '+str(service)+' in '+str(self.reference_VM_type)+' performance targets')
        service_l = list()
        service_l.append(service)
        try:
              experiment.meets_performance_service(service_l,self.reference_VM_type,service)
              self.store_performance_targets(service)
              self.target_dict = self.load_performance_targets()

        except Exception as e:
            logging.error("Performance data for service "+str(service)+" "+str(e)+" is missing")
            return None

    #****************************************************
    # Purpose: Reads from results.csv file 
    # Inputs:  results.csv file path
    # Returns: Returns a list with each row containing service and performance
    #**************************************************** 
    def read_service_performances(self):
        logging.debug('[targets] reading performance data from file '+str(self.results_file_path))
        rows = []
        with open(self.results_file_path) as in_file:
                reader = csv.DictReader(in_file)
                for row in reader:
                        try:
                            # Row already has all the information
                            # below steps are there only to convert fro types
                            service_combination_tup = parse_service_combination(row['service_combination'])
                            # only read single service entries
                            if len(service_combination_tup) != 1:
                                continue 
                            row['service_combination'] = service_combination_tup
                            row['performance_value(ms)'] = float(row['performance_value(ms)'])
                            rows.append(row)
                        except:
                            logging.error('Could not add\n{}\n'.format(row))
                            pass
        return rows

    #****************************************************
    # Purpose: Reads from results.csv file and calculates performance targets for all APIs in a service
    # Inputs:  Service for which we need the targets
    # Returns: Returns a list with each row containing api and its performance target
    #**************************************************** 
    def calculate_performance_targets(self,service):
          logging.debug('[targets] calculate performance targets for service'+str(service))
          rows = self.read_service_performances()
          
          perf_dict = {}
          for row in rows:
               api = row['API_name']
               service_t = row['service_name']
               performance = row['performance_value(ms)']
               vm_type = row['vm_type']     

               # we don't care if the VM type is not reference VM
               # or its not the required service
               if vm_type != self.reference_VM_type or service != service_t:
                   continue         
               
               if service_t not in perf_dict.keys():
                    perf_dict[service_t] = {}
               if api not in perf_dict[service_t].keys():
                    perf_dict[service_t][api] = []
           
               perf_dict[service_t][api].append(performance)

          perf_targets = []
          for service in perf_dict:
              for api in perf_dict[service]:
               row = {'service_name': service, 'API_name': api, 'performance_target(ms)': median(perf_dict[service][api])}
               perf_targets.append(row)
          return perf_targets

    #****************************************************
    # Purpose: Reads from results.csv file and updates targets.csv for a service
    # Inputs:  Service for which we need the targets
    # Returns: Writes to the targets.csv file
    #**************************************************** 
    def store_performance_targets(self,service):
          logging.debug('[results] Generating performances for {}'.format(ssot.get_app()))
          perf_targets = self.calculate_performance_targets(service)
          fieldnames = ['service_name','API_name','performance_target(ms)']
          with open(self.targets_file_path, 'a+') as out_file:
               writer = csv.DictWriter(out_file, fieldnames=fieldnames)
               writer.writerows(perf_targets)
    
    #****************************************************
    # Purpose: Reads from targets.csv file
    # Inputs:  targets_file_path: where is targets file stored
    # Returns: Returns a Dict with service -> api -> performance target
    #**************************************************** 
    def load_performance_targets(self):
        logging.debug('[targets] reading performance targets from file '+str(self.targets_file_path))
        res = {}
        with open(self.targets_file_path) as targets_file:
            reader = csv.DictReader(targets_file)
            for row in reader:
                try:
                    service = row['service_name']
                    api = row['API_name']
                    performance = float(row['performance_target(ms)'])

                    if service not in res:
                        res[service] = {}
                    service_to_api = res[service] # dictionary from service to api
                    service_to_api[api] = performance

                except Exception as e:
                    logging.error('Could not parse\n{}\n'.format(row))
                    logging.error(e)
                    pass
        return res
    
    #****************************************************
    # Purpose: Checks wheater a service's performance target is alread read to RAM
    # Inputs:  Service to check
    # Returns: Returns True if service is in RAM or False
    #****************************************************  
    def is_performance_target_exists(self, service):
        if service in self.target_dict.keys():
            return True
        return False
    
    #****************************************************
    # Purpose: Update internal data structure with the service data
    # Inputs:  Service to check
    # Returns: updates self.target_dict
    #****************************************************  
    def ensure_cache_is_updated(self,service):
        logging.debug('[targets] make sure performance targets are loaded to RAM for service '+str(service))
        # Make sure that performance targets are there in target_dict
        
        # First load from the file
        if not self.is_performance_target_exists(service):
            self.target_dict = self.load_performance_targets()

        # if value still not present recalculate from the results.csv
        if not self.is_performance_target_exists(service):
            self.store_performance_targets(service)
            self.target_dict = self.load_performance_targets() 
        
        # still doesn't exists ignore the check
        if service not in self.target_dict:
            self.target_dict[service] = {}
            self.target_dict[service]['api'] = 0
            logging.debug('service '+str(service)+' is ignored')
        # if not self.is_performance_target_exists(service):
        #      self.execute_experiments_for_performance_targets(service)
        #      return False # for unittests
        return True # for unittests
    
    #****************************************************
    # Purpose: get all the APIs in a service
    # Inputs:  service
    # Returns: Returns a list of APIs
    #****************************************************   
    def get_apis_in_a_service(self,service):
        logging.debug('[targets] get APIs for the service '+str(service))
        self.ensure_cache_is_updated(service) 
        if service in self.target_dict:
            return self.target_dict[service].keys()
    
    def get_services(self):
        return self.target_dict.keys()

    #****************************************************
    # Purpose: Retrive service's performance target if its there in target_dict
    # If the performance target doesn't exists it executes experiments and loads the data
    # Inputs:  Service for which performance target is needed
    # Returns: Returns a dict api -> performance target or None (if can't get any performance data)
    #****************************************************   
    def get_performance_target(self,service,api):
        logging.debug('[targets] get performance target for the service '+str(service)+' and API '+str(api)) 
        self.ensure_cache_is_updated(service) 
        # Retrive performance targets from target dict
        if service in self.target_dict and api in self.target_dict[service]:
             target_in_ms = self.target_dict[service][api]
             if target_in_ms == 0:
                 return 0
             else:
                return (1/target_in_ms)*ssot.get_target_offset() # some % of throughput
        else:
            return None
    

    def get_performance_target_in_execution_time(self,service,api):
        logging.debug('[targets] get performance target for the service '+str(service)+' and API '+str(api)) 
        self.ensure_cache_is_updated(service) 
        # Retrive performance targets from target dict
        if service in self.target_dict and api in self.target_dict[service]:
             target_in_ms = self.target_dict[service][api]
             if target_in_ms == 0:
                 return 0
             else:
                return (target_in_ms)*2 # some % of throughput
        else:
            return None

    #****************************************************
    # Purpose: Retrive performance targets for all services in service combination
    # Inputs:  Service combination for which performance target is needed
    # Returns: Returns a dictonary with service -> api -> performance target
    #****************************************************   
    def get_performance_targets(self, service_combination):
        logging.debug('[targets] get performance targets for the service '+str(service_combination)) 
        targets = {}
        for service in service_combination:
                targets[service] = self.get_performance_target(service)
        return targets
    
    def calculate_denominator(self,service_combination):
        logging.debug('[targets] calculate_denominator '+str(service_combination)) 
        targets = self.get_performance_targets(service_combination)
        sum_targets = 0
        for service in targets:
                for api in targets[service]:
                    target = int(targets[service][api])
                    sum_targets = sum_targets + target
        if sum_targets == 0:
            sum_targets = 1
        return sum_targets

performance_targets = performance_targets()
