import csv
import sys
sys.path.append('../SSOT')
sys.path.append('../../../SSOT') #for running unittests
from conf import ssot
import copy
import subprocess
import results_controller
from plot import plot
import os
import logging
import collections

class vm_type_selector_trace:
    def init(self,vm_type_selector,propagation_mode,budget,results_controller,services=None):
        logging.config.fileConfig('/wd/code/SSOT/logging.conf')
        self.filename = '/wd/code/apps/'+ssot.get_app()+'/Traces/'+str(vm_type_selector)+'_'+str(propagation_mode)+'_'+str(ssot.get_target_offset())+'.csv'
        self.services=services
        self.is_executed_index = 0
        self.service_comb_index = 1
        self.vm_type_name_index = 2
        self.meets_index = 3
        self.results_controller = results_controller
        self.is_write_mode = False
        self.last_combination_executed = ''
    
    def trace_exists(self):
        if not self.is_write_mode:
            return os.path.isfile(self.filename)
        else:
            return False

    def set_write_mode(self):
        self.is_write_mode = True
        subprocess.call(['rm -r '+self.filename], shell=True)

    def add_trace(self,exe_type,sc,vm_type,meets_perf):
        if self.is_write_mode:
            file = open(self.filename, mode='a+')
            writer = csv.writer(file)
            writer.writerows([[exe_type, sc, vm_type['name'], meets_perf]])
            file.close()

    def get_raw_data(self):
            num_experiment = 0
            search_cost = 0
            results_cache = {}
            results_list = []

            with open(self.filename) as f:
                    reader = csv.reader(f)
                    # Each row corresponds to a service combination -> VM type execution
                    # Row structure: Propagation (True/False) ; Service combination (('s1','s2')) ; VM_type_name; price of the VM
                    for row in reader:
                            #logging.info()
                            # extract data
                            is_executed = row[self.is_executed_index]
                            
                            # Remove quotes in service combination string 
                            row[self.service_comb_index] = row[self.service_comb_index][1:]
                            row[self.service_comb_index] = row[self.service_comb_index][:-1]
                            
                            # convert it into tuple
                            list_obj = [x.strip().replace("u'",'').replace("'",'') for x in row[self.service_comb_index].split(',')]
                            service_combination = tuple(list_obj)
                            
                            if len(service_combination) == 2: # special case for one service combinations
                                if service_combination[1] == '':
                                    service = service_combination[0] 
                                    service_l = list()
                                    service_l.append(str(service))
                                    service_combination = tuple(service_l)

                            vm_name = row[self.vm_type_name_index]
                            vm_cost = ssot.get_vm_cost(vm_name)
                            vm_type = ssot.get_vm(vm_name)
                            meets_performace = row[self.meets_index]
                            
                            if meets_performace == 'True': 
                                meets_perf = True
                            else:
                                meets_perf = False
                            
                            if service_combination not in results_cache.keys():
                                results_cache[service_combination] = {}
                            
                            if is_executed == 'True':
                                is_executed = True
                            else:
                                is_executed = False
                                
                            results_cache[service_combination][vm_name] = (meets_perf,is_executed)
                            results_list.append((service_combination,vm_name,meets_perf,is_executed))

            return results_list

    def get_results_cache(self,budget):
            # parameters to return
            num_experiment = 0
            search_cost = 0
            results_cache = {}
            count_comb = {}

            with open(self.filename) as f:
                    reader = csv.reader(f)
                    # Each row corresponds to a service combination -> VM type execution
                    # Row structure: Propagation (True/False) ; Service combination (('s1','s2')) ; VM_type_name; price of the VM
                    for row in reader:
                    
                            # extract data
                            is_executed = row[self.is_executed_index]
                            
                            # Remove quotes in service combination string 
                            row[self.service_comb_index] = row[self.service_comb_index][1:]
                            row[self.service_comb_index] = row[self.service_comb_index][:-1]
                            
                            # convert it into tuple
                            list_obj = [x.strip().replace("u'",'').replace("'",'') for x in row[self.service_comb_index].split(',')]
                            service_combination = tuple(list_obj)

                            if len(service_combination) == 2: # special case for one service combinations
                                if service_combination[1] == '':
                                    service = service_combination[0] 
                                    service_l = list()
                                    service_l.append(str(service))
                                    service_combination = tuple(service_l)
                
                            
                            # if len(service_combination) > 1:
                            #     continue

                            vm_name = row[self.vm_type_name_index]
                            vm_cost = ssot.get_vm_cost(vm_name)
                            vm_type = ssot.get_vm(vm_name)
                            meets_performace = row[self.meets_index]
                            
                            if meets_performace == 'True': 
                                meets_perf = True
                            else:
                                meets_perf = False

                            # count only when executed
                            if is_executed == 'True':
                                if (budget-vm_cost) < 0:
                                        break
                                num_experiment = num_experiment + 1
                                search_cost = search_cost + vm_cost
                                self.results_controller.add_experiment(True,service_combination,vm_type,meets_perf)
                                budget = budget - vm_cost

                                if meets_perf:
                                    if service_combination not in count_comb.keys():
                                        count_comb[service_combination] = []

                                    count_comb[service_combination].append(vm_name)

                            else:
                                self.results_controller.add_experiment(False,service_combination,vm_type,meets_perf)
                            
                            self.last_combination_executed = service_combination
                            
                            if meets_perf:
                                best_vm_type = ssot.get_vm(vm_name)
                                if best_vm_type != None:
                                    if service_combination not in results_cache.keys():
                                        results_cache[service_combination] = best_vm_type 
                                    else:
                                        if results_cache[service_combination]['price'] > vm_cost:
                                            results_cache[service_combination] = best_vm_type
                        

            # count_dict = {}
            # for combination in count_comb.keys():
            #     # print combination
            #     if len(combination) not in count_dict.keys():
            #         count_dict[len(combination)] = {}
             
            #     for vm_name in count_comb[combination]:
            #         # print combination,vm_name
            #         vm_name = ssot.get_VM_nick_name(vm_name)
            #         # print vm_name
            #         if vm_name in count_dict[len(combination)].keys():
            #             count_dict[len(combination)][vm_name] = count_dict[len(combination)][vm_name] + 1
            #         else:
            #             count_dict[len(combination)][vm_name] = 1
            
            # for combination in count_dict.keys():
            #     d = count_dict[combination]
            #     count_dict[combination] = collections.OrderedDict(sorted(d.items()))
            
            # for combination,values in count_dict.items():
            #     print combination
            #     sum = 0
            #     for key,value in values.items():
            #         print key+' : '+str(value)
            #         sum = sum + value
            #     print sum

            count_dict = {}
            for combination in count_comb:
                if len(combination) not in count_dict.keys():
                    count_dict[len(combination)] = 1
                else:
                    count_dict[len(combination)] = count_dict[len(combination)] + 1
            print count_dict
     
            return results_cache
#PopulationBasedSearch(services,results_cache).solve()
vm_trace_logger = vm_type_selector_trace()