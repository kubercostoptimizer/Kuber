import csv
import logging
import sys
sys.path.append('../SSOT')
from conf import ssot

def parse_service_combination(service_combination_str):
          splitted_tokens = service_combination_str.split("'")
          return tuple(splitted_tokens[1::2])  

def read_performances(results_file_path):
        res = {}
        with open(results_file_path) as results_file:
            reader = csv.DictReader(results_file)
            for row in reader:
                try:
                    vm = row['vm_type']
                    service_combination_tup = parse_service_combination(row['service_combination'])
                    service = row['service_name']
                    api = row['API_name']
                    performance = round(float(row['performance_value(ms)']),1)

                    if vm not in res:
                        res[vm] = {}
                    vm_to_sc = res[vm] # dictionary from service combination to service
                    if service_combination_tup not in vm_to_sc:
                       vm_to_sc[service_combination_tup] = {}
                    sc_to_service = vm_to_sc[service_combination_tup] # dictionary from service to api
                    if service not in sc_to_service:
                       sc_to_service[service] = {}
                    service_to_api = sc_to_service[service] 
                    service_to_api[api] = performance

                except Exception as e:
                    logging.error('In read performances, could not parse\n{}\n'.format(row))
                    logging.error(e)
                    pass
        
        return res

def read_performance_targets(targets_file_path):
        res = {}

        with open(targets_file_path) as targets_file:
            reader = csv.DictReader(targets_file)
            for row in reader:
                try:
                    service = row['service_name']
                    api = row['API_name']
                    performance = round(float(row['performance_target(ms)']),1)

                    if service not in res:
                        res[service] = {}
                    service_to_api = res[service] # dictionary from service to api
                    service_to_api[api] = performance

                except:
                    logging.error('Could not parse\n{}\n'.format(row))
                    pass
        return res

performance_data = read_performances('data.csv')
perf_targets = read_performance_targets('perf_targets.csv')

outfile = open('dataout.csv', 'a+')
fieldnames = ['service_combination','satisfies','cpu','computer','ram']
writer = csv.DictWriter(outfile, fieldnames=fieldnames)

dataout_t = []
for vm_type in performance_data.keys():
    for service_combination in performance_data[vm_type].keys():
        satisfies = True
        for service in performance_data[vm_type][service_combination].keys():
            for api in performance_data[vm_type][service_combination][service].keys():
                if service in perf_targets and api in perf_targets[service]:
                    if perf_targets[service][api] < performance_data[vm_type][service_combination][service][api]:
                        satisfies = False
        if ssot.get_vm_type_attr(vm_type) is not None:
            row_t = {'service_combination':service_combination,'satisfies':satisfies}
            row_t.update(ssot.get_vm_type_attr(vm_type))
            dataout_t.append(row_t)

writer.writerows(dataout_t)
outfile.close()