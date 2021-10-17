import csv
import sys
import json
import logging
from util import *
sys.path.append('../../../SSOT') #for unittests
sys.path.append('../SSOT')
from conf import ssot
from numpy import median
sys.path.append('../../../Profiler') #for unittests
sys.path.append('../Profiler')
from profiler import Profiler
from test_infra import infra

"""
Interface
1. relevant_meets_perf(current_combination,relavent_combination,vm_type) 
2. meets_performance(service_combination,vm_type) 
"""
class experiment:
    
    BASE_FOLDER = '../../code'  
    FOLDER_CHARACTER = '/'  

    def __init__(self):
    
        self.results_file_path = FOLDER_CHARACTER.join([ssot.get_app_path(), '/result','Data', 'results.csv'])

        self.metrics_file_path = FOLDER_CHARACTER.join([ssot.get_app_path(), '/result','Data', 'results_metrics.csv'])
        
        # vm type -> service combination -> service -> api -> performance
        self.perf_dict = self.load_performances()

        self.metrics_dict = self.load_metrics()

        self.num_repeatitions = 3



    def load_metrics(self):
        logging.debug('[Experiment] loading metrics data from file '+str(self.metrics_file_path))
        res = {}
        line_number = 0
        with open(self.metrics_file_path) as metrics_file:
            reader = csv.DictReader(metrics_file)
            for row in reader:
                try:
                    line_number = line_number + 1
                    
                    # read rows from the file
                    vm = row['vm_type']
                    service_combination_tup = parse_service_combination(row['service_combination'])
                    index = int(row['index'])
                    metric = []
                    
                    cpu_idle = float(row['cpu_idle'])
                    cpu_user = float(row['cpu_user'])
                    cpu_sys = float(row['cpu_sys'])

                    mem = float(row['mem'])
                    cache = float(row['cache'])
                    buffer = float(row['buffer'])

                    procs_running = float(row['procs_running'])
                    procs_blocked = float(row['procs_blocked'])
                    
                    load1 = float(row['load1'])
                    load5 = float(row['load5'])
                    load15 = float(row['load15'])

                    metric.append(cpu_idle)
                    metric.append(cpu_user)
                    metric.append(cpu_sys)
                    metric.append(mem)
                    metric.append(cache)
                    metric.append(buffer)
                    metric.append(procs_running)
                    metric.append(procs_blocked)
                    metric.append(load1)
                    metric.append(load5)
                    metric.append(load15)

                    if vm not in res:
                        res[vm] = {}
                    if service_combination_tup not in res[vm]:
                        res[vm][service_combination_tup] = {} # dictionary from service combination to service
                    if index not in res[vm][service_combination_tup]:
                        res[vm][service_combination_tup][index] = {} 
                    
                    res[vm][service_combination_tup][index] = metric

                except Exception as e:
                    logging.error('could not parse '+str(row)+' in line '+str(line_number))
                    logging.error(e)
                    pass
        
        return res

    def get_metrics(self,index,vm_name, service_combination):
        if vm_name in self.metrics_dict.keys():
            if service_combination in self.metrics_dict[vm_name].keys():
                if index in self.metrics_dict[vm_name][service_combination].keys():
                    return self.metrics_dict[vm_name][service_combination][index]
                else:
                    return None
            else:
                return None
        else:
            return None

    """
    Purpose: Loads performance data from self.results_file_path
    Input  : Results file path
    Output : Dict containing vm -> service_combination -> service -> api -> performance
    """
    def load_performances(self):
        logging.debug('[Experiment] loading performance data from file '+str(self.results_file_path))
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
                    logging.error('could not parse '+str(row)+' in line '+str(line_number))
                    logging.error(e)
                    pass
        
        return res

    def is_complete_exper_data_exists(self,vm_name,service_combination):
        for index in range(0,self.num_repeatitions):
            if not self.is_experiment_data_exists(index,vm_name,service_combination):
                   return False
        return True

    def is_experiment_data_exists(self, index,vm_name, service_combination):
        logging.debug('[Experiment] does experiment data exists for combination '+str(service_combination)+' on '+str(vm_name))
        if vm_name in self.perf_dict.keys():
            if service_combination in self.perf_dict[vm_name].keys():
                if index in self.perf_dict[vm_name][service_combination].keys():
                    # for service in service_combination:
                    #     if service not in self.perf_dict[vm_name][service_combination][index].keys():
                    #         return False
                    #     else:
                    #         from targets import performance_targets
                    #         for api in performance_targets.get_apis_in_a_service(service):
                    #             if api not in self.perf_dict[vm_name][service_combination][index][service].keys():
                    #                 return False
                    return True
        return False
    """
    Purpose: find a API in a service ran as a service combination on a vm meets target
    Input  : Combination, Service, API, and VM_type
    Output : True -> if API meets performance targets, else False
    None: if there is an error executing the experiment
    """ 
    def meets_performance_api(self,index,service_combination,vm_name,service,api,do_not_execute=False):

        logging.debug('[Experiment] verifying API'+str(api)+' in service '+str(service)+' in service combination '+str(service_combination)+' meets performance on '+str(vm_name)) 
        from targets import performance_targets

        target = performance_targets.get_performance_target(service,api)

        if target == 0:
            logging.debug('Target is Zero for service '+str(service)+' api '+str(api))
            return True

        # we repeat experiment for 3 times to get result
        perf = self.get_performance(index,vm_name,service_combination,service,api,do_not_execute)
        
        # performance values are too low
        if perf == 0:
            return True
            
        # data is incomplete re-execute the experiment
        if perf is None:
            return None
        
        if perf < target:
            return False
        else:
            return True
 
    """
    Purpose: find a service ran as a service combination on a vm meets target
    Input  : Combination, Service, and VM_type
    Output : True -> if all APIs in the service meets performance targets, else False
    None: if there is an error executing the experiment
    """ 
    def meets_performance_service(self,index,service_combination,vm_name,service,do_not_execute=False):
         logging.debug('[Experiment] verifying service '+str(service)+' in service combination '+str(service_combination)+' meets performance on '+str(vm_name)) 
         from targets import performance_targets
         # find how many apis in the service
         apis = performance_targets.get_apis_in_a_service(service)
         meets_perf_g = None
         for api in apis:
             meets_perf = self.meets_performance_api(index,service_combination,vm_name,service,api,do_not_execute)
             if meets_perf is False:
                # logging.info(str(api))
                return False
             elif meets_perf is None:
                  meets_perf_g = None
             elif meets_perf is True:
                  meets_perf_g = True
         return meets_perf_g
    
    """
    Purpose: if single service doesn't satisfy performance no combination does
    this function is here to check that
    Input  : Service and VM_type
    Output : True -> if all APIs meets performance targets, else False
    """ 
    def does_service_meets_perf(self,index,service,vm_name):
        logging.debug('[Experiment] verifying service '+str(service)+' meets performance on '+str(vm_name)) 
        if not isinstance(service,tuple):
            service_l = list()
            service_l.append(str(service))
            service_l = tuple(service_l)
        else:
            service_l = service 
        
        # all APIs in these common services should satisfy the performance target
        return self.meets_performance_service(index,service_l,vm_name,service)

    """
    Purpose: above function applied to all services in the combination
    Input  : Combination and VM_type
    Output : True -> if all APIs meets performance targets, else False
    """  
    def does_services_meet_perf(self,service_combination,vm_name):
        logging.debug('[Experiment] verifying if each service alone meets performance')
        for index in range(0,self.num_repeatitions):
            for service in service_combination:
                if not self.does_service_meets_perf(index,service,vm_name):
                    logging.info('Single service: '+str(service)+' vm_name '+str(vm_name)+' index '+str(index)+' does not meet the target')
                    return False
        return True

    def meets_performance_for_index(self, index, service_combination, vm_name, do_not_execute=False):
        logging.debug('[Experiment] running '+str(service_combination)+' on '+str(vm_name)) 
        # Optimization to reduce number of executions
        # if single services in this service combination didn't meet targets then others don't
        # if not self.does_services_meet_perf(service_combination,vm_name):
        #          return False
        if len(service_combination) == 1 and vm_name == 'M6.2xlarge': # single service always works on largest VM type
            return True

        for service in service_combination:
            if not self.is_experiment_data_exists(index,vm_name,service_combination):
                    self.perf_dict = self.load_performances()


            if not self.is_experiment_data_exists(index,vm_name,service_combination) and do_not_execute: # their is do not execute enabled but we don't have data
                    return None

            if not self.meets_performance_service(index,service_combination,vm_name,service,do_not_execute):
                    logging.debug('Service: '+str(service)+' vm_name '+str(vm_name)+' index '+str(index))
                    return False
        return True

    """
    Purpose: Tells a combination satisfies target on a VM
    Input  : Combination and VM_type
    Output : True -> if all APIs meets performance targets, else False
    """  
    def meets_performance(self, service_combination, vm_name, do_not_execute=False):
        logging.debug('[Experiment] running '+str(service_combination)+' on '+str(vm_name)) 
        # Optimization to reduce number of executions
        # if single services in this service combination didn't meet targets then others don't
        # if not self.does_services_meet_perf(service_combination,vm_name):
        #          return False
        if len(service_combination) == 1 and vm_name == 'M6.2xlarge': # single service always works on largest VM type
            return True

        for index in range(0, self.num_repeatitions):
            for service in service_combination:
                if not self.is_experiment_data_exists(index,vm_name,service_combination):
                        self.perf_dict = self.load_performances()

                # their is do not execute enabled but we don't have data
                if not self.is_experiment_data_exists(index,vm_name,service_combination): #and do_not_execute:  
                        #return None
                        return False # remove it

                if not self.meets_performance_service(index,service_combination,vm_name,service,do_not_execute):
                        logging.debug('Service: '+str(service)+' vm_name '+str(vm_name)+' index '+str(index))
                        return False
        return True
        
    """
    Purpose: Check if a relavent combination meets performance target for APIs in current combination 
    Input  : Current and Relavent combinations are tuples of services.
             vm_type is where we have to compare performance of services in relavent combination to targets
    Output : True -> if all APIs meets performance targets, else False
    """
    def relevant_meets_perf(self,current_combination,relavent_combination,vm_name):
        logging.debug('[Experiment] checking relevent meets current '+str(current_combination)+' with '+str(relavent_combination)+' on '+str(vm_name))
        # We need to extract common services from Current and Relavent combination
        common_services = tuple(set(current_combination) & set(relavent_combination))
        # if ntg in common return false
        if len(common_services) == 0:
            return None

        # for index in range(0,self.num_repeatitions):
        #     for service in common_services:
        #         # Optimization to reduce number of executions
        #         # if single services in this service combination didn't meet targets then others don't
        #         if not self.does_service_meets_perf(index,service,vm_name):
        #             return False

   
        for index in range(0,self.num_repeatitions):
            if not self.is_experiment_data_exists(index,vm_name,relavent_combination): # their is do not execute enabled but we don't have data
                return None
            # all APIs in these common services should satisfy the performance target
            for service in common_services:            
                if not self.meets_performance_service(index,relavent_combination,vm_name,service,True):
                    logging.debug(str(index)+' '+str(service)+' '+str(vm_name))
                    return False

        return True

    """
    Purpose: This method is only used by BO to calculate its cost function 
    Input  : combination and VM type
    Output : sum of all performance values
    """
    def get_denominator(self,vm_type,service_combination):
            denom_array = []
            for service in targets:
                    api_dict = targets[service]
                    for api in api_dict:
                        target = round(float(api_dict[api]),1)
                        if service in performances and api in performances[service]:
                            perf = round(float(performances[service][api]),1)
                            logging.debug('service '+str(service)+' '+'perf '+str(perf)+' target '+str(target)+' value '+str(perf - target - EPS))
                        else:
                            perf = 1
                        denom = max(perf, target)
                        if denom ==0: denom = 1
                        denom_array.append(1/denom)

            denominator = 0
            for denom in denom_array:
                denominator += denom
            if denominator == 0:
                # no perf target
                denominator = 1
    
    def execute_profiler(self,index,vm_name,service_combination):
         if not self.is_experiment_data_exists(index,vm_name,service_combination): # experiment is not in the file execute
            logging.info("[Experiment] Executing for "+str(vm_name)+" "+str(service_combination)+" "+str(index))
            num_tries = 0
            while True:
                try:
                    Profiler.execute(index,vm_name,service_combination)
                    #exit()
                    self.perf_dict = self.load_performances()
                    if vm_name not in self.perf_dict.keys() or service_combination not in self.perf_dict[vm_name].keys() or index not in self.perf_dict[vm_name][service_combination].keys():
                        logging.error('[Experiment] Data is missing repeating the experiment')
                        num_tries = num_tries + 1
                        if num_tries >= 3:
                            logging.error('[Experiment] Data is missing, we repeated the experiment 3 times still have some issue')
                            logging.error('[Experiment] Re-deploying the app for a reset')
                            #re-deploy the app
                            infra.redeploy()
                        continue
                    break
                except Exception as e:
                    logging.error('Exception repeating the experiment :(')
                    logging.error(e)

         return self.perf_dict
         
    """
    Purpose: Run and get performance values if they don't already exists in the perf_dict
    Input  : combination, service, api, and VM type
    Output : Throughput
    """
    def get_performance(self, index, vm_name, service_combination, service, api,do_not_execute=False):
        if not self.is_experiment_data_exists(index,vm_name,service_combination):
            self.perf_dict = self.load_performances() # try to load from the file

        if not do_not_execute:
            self.perf_dict = self.execute_profiler(index,vm_name,service_combination)
          

        logging.debug("[Experiment] Reading performance data for "+str(service_combination)+" on "+str(vm_name)+" for index "+str(index))
        if vm_name in self.perf_dict:
            if service_combination in self.perf_dict[vm_name]:
                if index in self.perf_dict[vm_name][service_combination]:
                    if service in self.perf_dict[vm_name][service_combination][index]: 
                        if api in self.perf_dict[vm_name][service_combination][index][service]:
                            perf = self.perf_dict[vm_name][service_combination][index][service][api]
                            if perf == 0:
                                return 0
                            else:
                                logging.debug(str(api)+' '+str(service)+' '+str(perf))
                                return 1/perf # throughput
                        else:
                            logging.debug("[experiment] API "+str(api)+" not present")
                            return None
                    else:
                        logging.debug("[experiment] service "+str(service)+" not present")
                        return None
                else:
                    logging.debug("[experiment] index "+str(index)+" not present")
                    return None     
            else:
                logging.debug("[experiment] service combination "+str(service_combination)+" not present")
                return None
        else:
            logging.debug("[experiment] VM type "+str(vm_name)+" not present")
            return None

    """
    Purpose: Run and get performance values if they don't already exists in the perf_dict
    Input  : combination, service, api, and VM type
    Output : Throughput
    """
    def get_execution_time(self, index, vm_name, service_combination, service, api,do_not_execute=False):
        if not self.is_experiment_data_exists(index,vm_name,service_combination):
            self.perf_dict = self.load_performances() # try to load from the file
        
        if not do_not_execute:
            self.perf_dict = self.execute_profiler(index,vm_name,service_combination)
          
        logging.debug("[Experiment] Reading performance data for "+str(service_combination)+" on "+str(vm_name)+" for index "+str(index))
        if vm_name in self.perf_dict.keys():
            if service_combination in self.perf_dict[vm_name]:
                if index in self.perf_dict[vm_name][service_combination]:
                    if service in self.perf_dict[vm_name][service_combination][index]: 
                        if api in self.perf_dict[vm_name][service_combination][index][service]:
                            perf = self.perf_dict[vm_name][service_combination][index][service][api]
                            if perf == 0:
                                logging.debug('[Experiment] result: '+str(0))
                                return 0
                            else:
                                logging.debug('[Experiment] result: '+str(perf))
                                return perf # throughput
                        else:
                            logging.debug("[experiment] API "+str(api)+" not present")
                            return None
                    else:
                        logging.debug("[experiment] service "+str(service)+" not present")
                        return None
                else:
                    logging.debug("[experiment] index "+str(index)+" not present")
                    return None     
            else:
                logging.debug("[experiment] service combination "+str(service_combination)+" not present")
                return None
        else:
            logging.debug("[experiment] VM type "+str(vm_name)+" not present")
            return None

experiment = experiment()


# Profiler.execute(5,'M6.2xlarge',('comservice1','comservice2','comservice3'))
# Profiler.execute(5,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4'))
# #Profiler.execute(0,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4','comservice5'))

# Profiler.execute(6,'M6.2xlarge',('comservice1','comservice2','comservice3'))
# Profiler.execute(6,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4'))
# #Profiler.execute(1,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4','comservice5'))

# Profiler.execute(7,'M6.2xlarge',('comservice1','comservice2','comservice3'))
# Profiler.execute(7,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4'))
# #Profiler.execute(2,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4','comservice5'))

# Profiler.execute(8,'M6.2xlarge',('comservice1','comservice2','comservice3'))
# Profiler.execute(8,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4'))
# #Profiler.execute(3,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4','comservice5'))

# Profiler.execute(9,'M6.2xlarge',('comservice1','comservice2','comservice3'))
# Profiler.execute(9,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4'))
# #Profiler.execute(4,'M6.2xlarge',('comservice1','comservice2','comservice3','comservice4','comservice5'))


# Profiler.execute(0,'M6.2xlarge',('geo',))
# Profiler.execute(1,'M6.2xlarge',('geo',))
# Profiler.execute(2,'M6.2xlarge',('geo',))
# Profiler.execute(3,'M6.2xlarge',('geo',))
# Profiler.execute(4,'M6.2xlarge',('geo',))

# Profiler.execute(0,'M6.2xlarge',('frontend',))
# Profiler.execute(1,'M6.2xlarge',('frontend',))
# Profiler.execute(2,'M6.2xlarge',('frontend',))
# Profiler.execute(3,'M6.2xlarge',('frontend',))
# Profiler.execute(4,'M6.2xlarge',('frontend',))

# Profiler.execute(0,'M6.2xlarge',('profile',))
# Profiler.execute(1,'M6.2xlarge',('profile',))
# Profiler.execute(2,'M6.2xlarge',('profile',))
# Profiler.execute(3,'M6.2xlarge',('profile',))
# Profiler.execute(4,'M6.2xlarge',('profile',))

# Profiler.execute(0,'M6.2xlarge',('rate',))
# Profiler.execute(1,'M6.2xlarge',('rate',))
# Profiler.execute(2,'M6.2xlarge',('rate',))
# Profiler.execute(3,'M6.2xlarge',('rate',))
# Profiler.execute(4,'M6.2xlarge',('rate',))

# Profiler.execute(0,'M6.2xlarge',('recommendation',))
# Profiler.execute(1,'M6.2xlarge',('recommendation',))
# Profiler.execute(2,'M6.2xlarge',('recommendation',))
# Profiler.execute(3,'M6.2xlarge',('recommendation',))
# Profiler.execute(4,'M6.2xlarge',('recommendation',))

# Profiler.execute(0,'M6.2xlarge',('reservation',))
# Profiler.execute(1,'M6.2xlarge',('reservation',))
# Profiler.execute(2,'M6.2xlarge',('reservation',))
# Profiler.execute(3,'M6.2xlarge',('reservation',))
# Profiler.execute(4,'M6.2xlarge',('reservation',))

# Profiler.execute(0,'M6.2xlarge',('search',))
# Profiler.execute(1,'M6.2xlarge',('search',))
# Profiler.execute(2,'M6.2xlarge',('search',))
# Profiler.execute(3,'M6.2xlarge',('search',))
# Profiler.execute(4,'M6.2xlarge',('search',))

# Profiler.execute(0,'M6.2xlarge',('user',))
# Profiler.execute(1,'M6.2xlarge',('user',))
# Profiler.execute(2,'M6.2xlarge',('user',))
# Profiler.execute(3,'M6.2xlarge',('user',))
# Profiler.execute(4,'M6.2xlarge',('user',))


# Profiler.execute(0,'M6.2xlarge',('user-service',))
# Profiler.execute(1,'M6.2xlarge',('user-service',))
# Profiler.execute(2,'M6.2xlarge',('user-service',))
# Profiler.execute(3,'M6.2xlarge',('user-service',))
# Profiler.execute(4,'M6.2xlarge',('user-service',))

# Profiler.execute(0,'M6.2xlarge',('social-graph-service',))
# Profiler.execute(1,'M6.2xlarge',('social-graph-service',))
# Profiler.execute(2,'M6.2xlarge',('social-graph-service',))
# Profiler.execute(3,'M6.2xlarge',('social-graph-service',))
# Profiler.execute(4,'M6.2xlarge',('social-graph-service',))

# Profiler.execute(0,'M6.2xlarge',('compose-post-service',))
# Profiler.execute(1,'M6.2xlarge',('compose-post-service',))
# Profiler.execute(2,'M6.2xlarge',('compose-post-service',))
# Profiler.execute(3,'M6.2xlarge',('compose-post-service',))
# Profiler.execute(4,'M6.2xlarge',('compose-post-service',))

# Profiler.execute(0,'M6.2xlarge',('post-storage-service',))
# Profiler.execute(1,'M6.2xlarge',('post-storage-service',))
# Profiler.execute(2,'M6.2xlarge',('post-storage-service',))
# Profiler.execute(3,'M6.2xlarge',('post-storage-service',))
# Profiler.execute(4,'M6.2xlarge',('post-storage-service',))

# Profiler.execute(0,'M6.2xlarge',('user-timeline-service',))
# Profiler.execute(1,'M6.2xlarge',('user-timeline-service',))
# Profiler.execute(2,'M6.2xlarge',('user-timeline-service',))
# Profiler.execute(3,'M6.2xlarge',('user-timeline-service',))
# Profiler.execute(4,'M6.2xlarge',('user-timeline-service',))

# Profiler.execute(0,'M6.2xlarge',('write-home-timeline-service',))
# Profiler.execute(1,'M6.2xlarge',('write-home-timeline-service',))
# Profiler.execute(2,'M6.2xlarge',('write-home-timeline-service',))
# Profiler.execute(3,'M6.2xlarge',('write-home-timeline-service',))
# Profiler.execute(4,'M6.2xlarge',('write-home-timeline-service',))

# Profiler.execute(0,'M6.2xlarge',('home-timeline-service',))
# Profiler.execute(1,'M6.2xlarge',('home-timeline-service',))
# Profiler.execute(2,'M6.2xlarge',('home-timeline-service',))
# Profiler.execute(3,'M6.2xlarge',('home-timeline-service',))
# Profiler.execute(4,'M6.2xlarge',('home-timeline-service',))

# Profiler.execute(0,'M6.2xlarge',('media-service',))
# Profiler.execute(1,'M6.2xlarge',('media-service',))
# Profiler.execute(2,'M6.2xlarge',('media-service',))
# Profiler.execute(3,'M6.2xlarge',('media-service',))
# Profiler.execute(4,'M6.2xlarge',('media-service',))

# Profiler.execute(0,'M6.2xlarge',('text-service',))
# Profiler.execute(1,'M6.2xlarge',('text-service',))
# Profiler.execute(2,'M6.2xlarge',('text-service',))
# Profiler.execute(3,'M6.2xlarge',('text-service',))
# Profiler.execute(4,'M6.2xlarge',('text-service',))

#Profiler.execute(0,'M6.2xlarge',('rating-service',))
# Profiler.execute(1,'M6.2xlarge',('rating-service',))
# Profiler.execute(2,'M6.2xlarge',('rating-service',))
# Profiler.execute(3,'M6.2xlarge',('rating-service',))
# Profiler.execute(4,'M6.2xlarge',('rating-service',))


#Profiler.execute(0,'M6.2xlarge',('unique-id-service',))
# Profiler.execute(1,'M6.2xlarge',('unique-id-service',))
# Profiler.execute(2,'M6.2xlarge',('unique-id-service',))
# Profiler.execute(3,'M6.2xlarge',('unique-id-service',))
# Profiler.execute(4,'M6.2xlarge',('unique-id-service',))

#Profiler.execute(0,'M6.2xlarge',('user-review-service',))
# Profiler.execute(1,'M6.2xlarge',('user-review-service',))
# Profiler.execute(2,'M6.2xlarge',('user-review-service',))
# Profiler.execute(3,'M6.2xlarge',('user-review-service',))
# Profiler.execute(4,'M6.2xlarge',('user-review-service',))

# Profiler.execute(0,'M6.2xlarge',('user-service',))
# Profiler.execute(1,'M6.2xlarge',('user-service',))
# Profiler.execute(2,'M6.2xlarge',('user-service',))
# Profiler.execute(3,'M6.2xlarge',('user-service',))
# Profiler.execute(4,'M6.2xlarge',('user-service',))

# print experiment.execute_profiler(0,'t3.micro',('comservice1', 'comservice2', 'comservice3', 'comservice4'))

# vm_types = copy.deepcopy(ssot.get_vm_names())
# for vm_name in vm_types:
#     for combination in ssot.get_service_combinations():
#        for index in range(0,15):
#          if not experiment.is_experiment_data_exists(index,vm_name,combination):
#             print index,vm_name,combination
#Profiler.execute(0,'M6.2xlarge',('comservice2',))
# Profiler.execute('a1.xlarge', (u'carts', u'orders', u'user'))
# Profiler.execute('a1.large',('payment', 'carts', 'orders', 'user'))
#print experiment.execute_profiler('M6.medium',('comservice5',))
# print experiment.execute_profiler('M6.large',('comservice5',))
# print experiment.execute_profiler('M6.xlarge',('comservice5',))
# print experiment.execute_profiler('M6.2xlarge',('comservice5',))
# print experiment.execute_profiler('M6.2xlarge',('orders',))
# print experiment.execute_profiler('M6.2xlarge',('user',))
# print experiment.execute_profiler('M6.2xlarge',('catalogue',))
