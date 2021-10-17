import json
import os
import sys
from itertools import combinations
import math
import logging.config
import logging
import copy
basePath = os.path.dirname(os.path.abspath(__file__))
configPath = basePath + "/config.json"


class conf:
    def __init__(self):
           with open(configPath) as data:
                 self.config = json.load(data)
           self.target_offset = 0.8
           self.base_app_path = '/wd/code/apps/' + self.get_app()
           logging.config.fileConfig('/wd/code/SSOT/logging.conf')
           self.services = self.config['Application']['services']

    def get_app_result_folder(self):
           return self.base_app_path + '/result'

    def get_app_state_folder(self):
           return self.base_app_path + '/state'
    
    def get_app_path(self):
           return self.base_app_path
           
    def analyze_kuber(self):
           return True
    
    def get_vm_selector(self):
           return self.config['Kuber']['vm_selector']
    
    def get_kuber_mode(self):
           return self.config['Kuber']['mode']
    
    def get_kuber_budget(self):
           return float(self.config['Kuber']['budget'])

    def get_front_end(self):
           return self.config['Application']['front-end']

    def get_precision(self):
           return int(self.config['Profiling']['analysis']['precision'])

    def get_time_limit(self):
           return self.config['Profiling']['load_gen']['time_limit']

    def get_outliers_removal(self):
           return int(self.config['Profiling']['analysis']['outliers_removal'])

    def get_percentile(self):
           return int(self.config['Profiling']['analysis']['percentile'])

    def get_throughput(self):
           return int(self.config['Profiling']['load_gen']['throughput'])

    def get_concurrent(self):
           return int(self.config['Profiling']['load_gen']['concurrent'])

    def get_vm_types(self):
           vm_types = self.config['Infrastructure']['vm_types']
           vm_types.sort(key=lambda x: x['price'])
           return copy.deepcopy(vm_types)

    def get_vm_names(self):
           return [vm['name'] for vm in self.get_vm_types()]

    def get_no_slave_vms(self):
           return int(self.config['Application']['no_slaves'])

    def set_target_offset(self, offset):
           with open(configPath, "r+") as jsonFile:
              data = json.load(jsonFile)

              data["Kuber"]["performance_target_offset"] = str(offset)

              jsonFile.seek(0)  # rewind
              json.dump(data, jsonFile)
              jsonFile.truncate()
           self.target_offset = offset

    def get_target_offset(self):
           with open(configPath, "r+") as jsonFile:
              data = json.load(jsonFile)
              self.target_offset = float(data["Kuber"]["performance_target_offset"])
           return self.target_offset

    def get_service_combinations_at_level(self,number_services):
           return combinations(self.services, number_services)


    def get_next_cheapest_vm(self,vm_name):
           current_price = self.get_vm_cost(vm_name)
           for vm in self.get_vm_types():
		if vm['price'] > current_price:
                   return vm


    def get_vm_cost(self, vm_name):
	   for vm in self.get_vm_types():
		if vm['name'] == vm_name:
                   return vm['price']

    def get_vm(self, vm_name):
	   for vm in self.get_vm_types():
		if vm['name'] == vm_name:
                   return vm

    def get_vm_attr(self, vm_name):
	   for vm in self.get_vm_types():
		if vm['name'] == vm_name:
		    return str(vm['cpu_count']), str(vm['ram']), str(vm['speed']), str(vm['computer'])

    def get_vm_features(self, vm_name):
	   for vm in self.get_vm_types():
		if vm['name'] == vm_name:
                     if vm['machine_type'] == 'mem':
                            machine_type = 1
                     else:
                            machine_type = 0

                     features = []
                     features.append(int(vm['cpu_count']))
                     features.append(int(vm['ram']))
                     features.append(machine_type)

                     return features

    def get_vm_type_attr(self,vm_name):
           for vm in self.get_vm_types():
		if vm['name'] == vm_name:
		    return {'cpu' : str(vm['cpu_count']), 'computer' : str(vm['machine_type']),'ram' : str(vm['ram'])}

    def get_port(self):
          return self.config['Application']['port']

    def get_services(self):
          return self.services

    def get_app(self):
           return self.config['Application']['name']

    def get_num_services(self):
           return len(self.get_services())

    def get_platform(self):
           return self.config['Infrastructure']['Cloud_provider']

    def get_immediate_children_for_combination(self,service_combination):
              services = list(service_combination)
              related_combinations = []
              for service_comb in combinations(services, len(service_combination)-1):
                     related_combinations.append(service_comb)
              return related_combinations

    def get_all_child_combinations(self,service_combination):
              services = list(service_combination)
              if len(services) == 2:
                     number_services = 2 #first element is empty
              else:
                     number_services = 1
              related_combinations = []
              while number_services <= len(services):
                     for service_comb in combinations(services, number_services):
                           related_combinations.append(service_comb)
                     number_services = number_services + 1
              return related_combinations
    
    def get_num_combinations(self):
           return pow(2,self.get_num_services())-1
    def get_service_combinations(self):
              number_services = 1
              services = self.get_services()
              service_combinations = list()
              while number_services <= len(services):
                     for service_comb in combinations(services, number_services):
                           service_combinations.append(service_comb)
                     number_services = number_services + 1
              return service_combinations

    def is_valid_vm_type(self,cpu, computer, ram):
       
         for vm_type in self.get_vm_types():
                  if vm_type['cpu_count'] == cpu and vm_type['ram'] == ram and vm_type['machine_type'] == computer:
                       return True
         return False

    def get_vm_name(self, cpu, computer, ram, disk_type='slow'):
           for vm_type in self.get_vm_types():
                  if vm_type['cpu_count'] == cpu and vm_type['ram'] == ram and vm_type['machine_type'] == computer:
                         return vm_type['name']

    def get_max_cost(self):
             total_price = 0
             for vm_type in self.get_vm_types():
                    total_price = total_price + vm_type['price']

             max_cost = math.pow(2, ssot.get_num_services()) * total_price

             return max_cost
     
    def get_VM_nick_name(self,vm_name):
           vm_names = self.get_vm_names()
           return 'VM'+str(vm_names.index(vm_name)+1)
  
ssot = conf()
