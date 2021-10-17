import os
import sys
from decimal import Decimal
sys.path.append('../SSOT')
from conf import ssot
sys.path.append('../Tools')
from timeout_command import timeout_command
import logging
from experiment import experiment

# Runs BO on one particular service combination
# Input: Tuple of services e.g. ('carts','orders')
# Output: Best VM type on which it works and map of VM types on which it tried and performance data
# Dependencies:
# run(): assumes BO has start.sh file and service combination will be given as environment variable
# output(): opens result file produced by BO

class BO:
    # Initialize BO
    # Pass service combinations and performance target
    def configure(self,service_combination):
            
            self.performance_target = experiment.get_performance_target(service_combination)
            self.service_combination = service_combination
            service_combination_str = ""
            # convert a service combination tuple to comma saparated string
            for service in service_combination:
                if service != '':
                    service_combination_str = service_combination_str+service+","    
            service_combination_str = service_combination_str[:-1]
            os.environ['services'] = service_combination_str
            os.environ['perf_target'] = str(self.performance_target)

    # Run for a service_combination;
    # Optional timeout 
    # showoutput : show logs
    def run(self,service_combination, timeout=100, showoutput=False):
        self.configure(service_combination)
        # Call cherrypick with timeout: if cherrypick can't decide on results after 100secs stop it
        # TODO: do we still need this? if so is 100 a correct number.
        # commnad, timeout, print output?
        timeout_command(['cd BO && sh start.sh'], timeout, showoutput)
        return self.output()

    # returns best vm type name after running BO
    def get_best_vm_type(self):
            best_vm = ''
            if os.path.exists("BO/best_job_and_result.txt"):
                with open("BO/best_job_and_result.txt", "r") as f:
                    contents = f.readlines()
                    cpu_count = [contents[4].split(":")[1].strip().strip('"')]
                    ram = [contents[6].split(":")[1].strip().replace('"', '')]
                    cpu_type = [contents[8].split(":")[1].strip().replace('"', '')]
                f.close()
                best_vm = ssot.get_vm_name(cpu_type, cpu_count, ram)
            return best_vm

    # returns map of vm_type_name => [order of exe, [price_str,performance,optvar]]
    # cheerypick specific details
    # Assumption: 5th line in BO/output/xxx.out should be of format
    # m4.4xlarge 0.8 21.3523131673 0.0374666666666
    def get_tried_vm_types(self):
            tried_VM_types = dict()
            # Read VM type on which cherrypick tried from /SDK/output folder
            for filename in os.listdir('BO/output'):
                try:
                    with open("BO/output/"+filename, "r") as f:
                        contents = f.readlines()
                       
                        result_str = contents[5].split(' ')
                        try:
                            VM_type_str = result_str[0]
                            price_str = Decimal(result_str[1])
                            performance_str = Decimal(result_str[2])
                            optvar_str = Decimal(result_str[3].strip('\n'))
                            tried_VM_types[VM_type_str] = [price_str, performance_str, optvar_str]
                        except:
                            print "Error while executing sc", self.service_combination
                finally:
                    f.close()

            experiments = dict()
            # Read order of experiments
            index = 0
            if os.path.exists("BO/cherrypick.log"):
                with open("BO/cherrypick.log") as f:
                    for trail in f.readlines():
                        result_str = trail.split(' ')
                        VM_index = int(result_str[0])
                        ei = float(result_str[1])
                        target_ei = float(result_str[2])
                        index = index + 1
                        # cherrypick.log will have last picked VM type but it would have executed because of ei < target_ei
                        # don't add final experiment as it is not executed
                        # not applicable for first experiment -> target_ei != 'nan\n'
                        if target_ei != 'nan\n' and ei < target_ei:
                            break
                        vm_types_names = ssot.get_vm_names()
                        vm_types_names.sort(key=ssot.get_vm_cost)
                        if (vm_types_names[VM_index] in tried_VM_types.keys()):
                            experiments[vm_types_names[VM_index]] = [index, tried_VM_types[vm_types_names[VM_index]], ei, target_ei, VM_index]
                    f.close()
            return experiments

    # just combines above two functions
    def output(self):
        # Read positive result from output file produced by cherrypick
        best_vm_type = self.get_best_vm_type()
        experiments = self.get_tried_vm_types()
        return experiments, best_vm_type
    
BO = BO()
