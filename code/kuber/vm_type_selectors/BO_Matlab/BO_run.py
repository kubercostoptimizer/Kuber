import os
import csv
import sys
import logging

sys.path.append('/wd/code/SSOT')
from conf import ssot
sys.path.append('/wd/code/kuber')
from targets import performance_targets
from experiment import experiment    # for BO unittests
from vm_trace_logger import vm_trace_logger
 
class BO_run:
    def __init__(self, service_combination, result_controller):
        logging.config.fileConfig('/wd/code/SSOT/logging.conf')
        self.service_combination = service_combination
        self.result_controller = result_controller
        self.best_vm = result_controller.get_best_vm(service_combination)
        self.local_optimization_cache = {}
        self.num_constraints = self.get_num_constriants()
        self.initial_vmtypes = ["t3.micro"]
        self.write_initial_VM_types()
        self.write_propagated_vm_types()
    
    """
    Purpose: check if the service combination meets performance target on VM type
    Input  : VM type 
    Output : -1 if meets performance target and +1 if doesn't for each API and cost of the VM type
    """   
    def meets_perf(self,cpu,speed,ram):
        try: 
            # # for BO unittests
            # experiment.results_file_path = '/wd/code/kuber/tests/UnitTests/test_files/result_file.csv'
            # experiment.targets_file_path = '/wd/code/kuber/tests/UnitTests/test_files/target_file.csv'
            # performance_targets.results_file_path = '/wd/code/kuber/tests/UnitTests/test_files/result_file.csv'
            # performance_targets.targets_file_path = '/wd/code/kuber/tests/UnitTests/test_files/target_file.csv'

            logging.info('[BO] Running VM type with '+str(cpu)+' '+str(speed)+' '+str(ram)) 
            if not ssot.is_valid_vm_type(cpu,speed,ram) or self.has_ran(cpu,speed,ram) or not self.should_run(cpu,speed,ram): # validation check and optimizations 
                logging.debug('not running VM type '+str(cpu)+' '+str(speed)+' '+str(ram))
                cost, constraints = self.get_data(cpu,speed,ram) # calculate return values without executing
                logging.debug('[BO] cost '+str(cost)+' constriants '+str(constraints))
                logging.info('------------------------------------------ Returning bad value or from cache --------------------------------------------')
                return cost,constraints
            
            
            # get all the data to execute the VM type
            vm_name = ssot.get_vm_name(cpu, speed, ram)
            vm_type = ssot.get_vm(vm_name)
            vm_cost = ssot.get_vm_cost(vm_name)
            logging.info('------------------------------------------'+str(vm_name)+'--------------------------------------------')
            
            if self.result_controller.get_result(self.service_combination,vm_type): # actual run
                constraints = [-1] * self.num_constraints
                meets_perf = True
            else:
                constraints = [1] * self.num_constraints
                meets_perf = False

            logging.debug('[BO] ran vm type '+str(vm_name)+' returning cost: '+str(vm_cost)+' constriants '+str(constraints))
            self.local_optimization_cache[vm_name] = [vm_cost,constraints] # if matlab re-executes same VM type, return from cache
            logging.info('-------------------------------------------------------------------------------------------')
            return vm_cost,constraints
            
        except Exception as e:
            logging.error('[BO_RUN] error occured: '+str(e))
 
    
    # Validity checks and optimizations
    def has_ran(self, cpu,speed,ram):
        vm_name = ssot.get_vm_name(cpu, speed, ram)
        vm_type = ssot.get_vm(vm_name)
        value = vm_name in self.local_optimization_cache.keys()
        if value:
            logging.info('[BO] already ran '+str(vm_name))
        return value

    def should_run(self, cpu,speed,ram):
        vm_name = ssot.get_vm_name(cpu, speed, ram)
        best_vm = self.result_controller.get_best_vm(self.service_combination)
        if best_vm is None:
            return True
        value = ssot.get_vm_cost(best_vm) > ssot.get_vm_cost(vm_name)
        if not value:
            logging.debug('[BO] current best is better so dont run on '+str(vm_name)) 
        return value
    
    def get_worst_cost(self):
        largest_vm_cost = ssot.get_vm_types()[-1]['price']
        EPS = 10 ** (-1) # small padding value
        return largest_vm_cost + EPS, [1] * self.num_constraints # return cost thats slightly larger than largest VM type
   
    def get_data(self,cpu,speed,ram):
        if not ssot.is_valid_vm_type(cpu,speed,ram) or not self.should_run(cpu,speed,ram):
            return self.get_worst_cost() 
        else:
            vm_name = ssot.get_vm_name(cpu, speed, ram)
            return self.local_optimization_cache[vm_name]
    
    def get_num_constriants(self):
        # we check performance targets per API
        # number should be equal to number of APIs
        num_constraints = 0 
        for service in self.service_combination:
            num_constraints += len(performance_targets.get_apis_in_a_service(service))
        return num_constraints

    def write_initial_VM_types(self):
        logging.info('[BO] writing initial vm types to files for BO '+str(self.initial_vmtypes)) 
        if os.path.isfile('VMtypes_to_propagate.csv'):
            os.remove('VMtypes_to_propagate.csv')
        vm_types_file = open('VMtypes_to_propagate.csv', mode='w')        
        fieldnames = ['cpu', 'computer', 'ram']

        vm_types_writer = csv.DictWriter(vm_types_file, fieldnames=fieldnames)
        vm_types_writer.writeheader()
        if len(self.result_controller.known_vm_types(self.service_combination)) == 0:
            for vm_name in self.initial_vmtypes:
                vm_types_writer.writerow(ssot.get_vm_type_attr(vm_name))
        else:
            for vm_type in self.result_controller.known_vm_types(self.service_combination):
                vm_types_writer.writerow(ssot.get_vm_type_attr(vm_type['name'])) 

        vm_types_file.close()

    # Interface with Matlab BO using files
    # Passing intial data such as propagated VM types
    def write_propagated_vm_types(self):
        
        if os.path.isfile('Objectives_to_propagate.csv'):
            os.remove('Objectives_to_propagate.csv')
        objectives_file = open('Objectives_to_propagate.csv', mode='w')
        objectives_writer = csv.writer(objectives_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        if os.path.isfile('Constriants_to_propagate.csv'):
            os.remove('Constriants_to_propagate.csv')
        constriants_file = open('Constriants_to_propagate.csv', mode='w')
        constriants_writer = csv.writer(constriants_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        for vm_type in self.result_controller.known_vm_types(self.service_combination):
            meets_perf = self.result_controller.get_propagated_result(self.service_combination,vm_type)
            self.result_controller.add_experiment(False,self.service_combination,vm_type,meets_perf)
            if meets_perf is None:
                continue
            elif meets_perf:
                constriants_writer.writerow([-1] * self.num_constraints)
                objectives_writer.writerow([vm_type])
                #/targets.calculate_denominator(self.service_combination)])
            else:
                constriants_writer.writerow([1] * self.num_constraints)
                objectives_writer.writerow([vm_type])
                #/targets.calculate_denominator(self.service_combination)
            
        objectives_file.close()
        constriants_file.close()
      