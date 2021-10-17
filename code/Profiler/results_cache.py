from stats import stats
from experiment_state import state
import csv
import numpy as np
import os
import subprocess
import sys
import logging
from Metrics_client import Metrics_client 
from numpy import median
sys.path.append('../SSOT')
from conf import ssot 

class results_cache:
    def __init__(self):
         self.csv_file_name = ssot.get_app_path()+"/result/Data/results.csv"
         self.metrics_file_name = ssot.get_app_path()+"/result/Data/results_metrics.csv"
         self.file = open(self.csv_file_name, mode='a+')
         self.fieldnames = ['exp_id','index','service_combination', 'vm_type', 'service_name','API_name','performance_value(ms)']
         self.fieldname_metric_file = ['exp_id','index','service_combination', 'vm_type', 'cpu_idle','cpu_user','cpu_sys','mem','cache','buffer','procs_running','procs_blocked','load1','load5','load15']
         self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
         sniffer = csv.Sniffer()
         has_header = sniffer.has_header(self.file.read(2048))
         self.file.seek(0)
         if not has_header:
              self.writer.writeheader()
         self.file.close()

         self.file = open(self.metrics_file_name, mode='a+')
         self.writer = csv.DictWriter(self.file, fieldnames=self.fieldname_metric_file)
         sniffer = csv.Sniffer()
         has_header = sniffer.has_header(self.file.read(2048))
         self.file.seek(0)
         if not has_header:
              self.writer.writeheader()
         self.file.close()


    def __del__(self):
         self.file.close()

    def get_all_operators(self,service):
          targets_file_path = ssot.get_app_path()+"/result/Data/performance_targets.csv"
          operators = []
          with open(targets_file_path) as targets_file:
               reader = csv.DictReader(targets_file)
               for row in reader:
                    service_t = row['service_name']
                    api = row['API_name']
                    if service == service_t:
                         operators.append(api)
          return operators

    def store_node_failure(self,vm_type,service_combination):
            self.file = open(self.csv_file_name, mode='a+')
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            exp_id = state.get_experiment_id(service_combination,vm_type)
            for service in service_combination:
              try:
                     for operator_name in self.get_all_operators(service):
                            exp_id_print = str(int(exp_id))
                            self.writer.writerow({'exp_id':int(exp_id_print),'index':str(0),'service_combination': tuple([str(s) for s in service_combination]), 'vm_type': vm_type, 'service_name': service, 'API_name': operator_name,'performance_value(ms)': 100000})
                                 
              except Exception as e:
                        logging.error(e)
                        logging.error("Results for service "+str(service)+" in experiment "+str(exp_id)+" are missing")
                        continue
            self.file.close()
  
    def store(self,index,vm_type,service_combination):
            self.file = open(self.csv_file_name, mode='a+')
            self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
            exp_id = state.get_experiment_id(service_combination,vm_type)
            for service in service_combination:
              perf_data = stats.get_exper_data(exp_id,service)
              try:
                     for operator_name, perf_list in perf_data.items():
                            if len(perf_data) > 1:
                              arry = stats.remove_outliers(np.array(perf_list))
                            else:
                              arry = np.array(perf_list) 
                            exp_id_print = str(int(exp_id))
                            if len(arry) == 0:
                                 logging.error(str(service)+' API: '+str(operator_name)+' array length is zero')
                                 self.writer.writerow({'exp_id':int(exp_id_print),'index':str(index),'service_combination': tuple([str(s) for s in service_combination]), 'vm_type': vm_type, 'service_name': service, 'API_name': operator_name,'performance_value(ms)': 0})
                                 continue
                            pers = np.percentile(arry, stats.percentile)
                            execution_time = round(pers/1000,stats.precision)
                            self.writer.writerow({'exp_id':int(exp_id_print),'index':str(index),'service_combination': tuple([str(s) for s in service_combination]), 'vm_type': vm_type, 'service_name': service, 'API_name': operator_name,'performance_value(ms)': execution_time})
                            logging.info("Results for service "+str(service)+" in experiment "+str(exp_id)+" are recorded")
              except Exception as e:
                        logging.error(e)
                        logging.error("Results for service "+str(service)+" in experiment "+str(exp_id)+" are missing")
                        continue
            self.file.close()
  
    def store_metrics(self,index,metrics_ip,vm_type,service_combination):
          try:
               self.file = open(self.metrics_file_name, mode='a+')
               self.writer = csv.DictWriter(self.file, fieldnames=self.fieldname_metric_file)
               exp_id = state.get_experiment_id(service_combination,vm_type)
               exp_id_print = str(int(exp_id))
               metrics = Metrics_client().get_data_for_query(metrics_ip,ssot.get_time_limit())
               self.writer.writerow({'exp_id':int(exp_id_print),'index':str(index),'service_combination': tuple([str(s) for s in service_combination]), 'vm_type': vm_type, 'cpu_idle': metrics[0],'cpu_user' : metrics[1],'cpu_sys' : metrics[2],'mem' : metrics[3],'cache' : metrics[4],'buffer' : metrics[5],'procs_running' : metrics[6],'procs_blocked' : metrics[7],'load1' : metrics[8],'load5' : metrics[9],'load15' : metrics[10]})
               self.file.close()
               logging.info("Metrics for expr "+str(service_combination)+" in experiment on "+str(vm_type)+" are recorded")
          except Exception as e:
                        logging.error(e)

#       def write_performance_to_csv_file(self,filename):
#                 with open(stats.state_folder+'/experiments.json') as json_file:
#                       data = json.load(json_file)
#                       with open(stats.state_folder+'/experiment_ids.json') as json_file_ids:
#                               not_executed_list = json.load(json_file_ids)
#                               with open(self.result_folder+'/'+filename, mode='a+') as csv_file:
#                                    for exp_id,experiment in data.items():
#                                           if int(exp_id) not in not_executed_list:
#                                                  vm_name = experiment[1]['name']                         
#                                                  services = experiment[0]
#                                                  for service in services:
#                                                         try:
#                                                                perf_data = self.get_exper_data(exp_id,service)
#                                                                for operator_name, perf_list in perf_data.items():
#                                                                       arry = self.remove_outliers(np.array(perf_list))
#                                                                       if len(arry) == 0:
#                                                                              continue
#                                                                       pers = np.percentile(arry, self.percentile)
#                                                                       execution_time = round(pers/1000.0,self.precision)
#                                                                       exp_id_print = str(int(exp_id))
#                                                                       writer.writerow({'exp_id':int(exp_id_print),'service_combination': tuple([str(s) for s in services]), 'vm_type': vm_name, 'service_name': service, 'API_name': operator_name,'performance_value(ms)': execution_time})
#                                                                       if not os.path.exists(self.result_folder+'/detailed_data'):
#                                                                              subprocess.call(['mkdir '+self.result_folder+'/detailed_data'], shell=True)
#                                                                       np.savetxt(self.result_folder+'/detailed_data/'+exp_id_print+'_'+service+'_'+operator_name.replace('/','')+'.csv', np.array(perf_list), delimiter=',')
#                                                         except IOError:
#                                                                print "Results for service ",service," in experiment ",exp_id," are missing"
#                                                                continue

results_cache = results_cache()
# results_cache.store('a1.medium',["social-graph-service"])
# results_cache.store('a1.large',["social-graph-service"])
# results_cache.store('a1.xlarge',["social-graph-service"])
# results_cache.store('a1.2xlarge',["social-graph-service"])

# results_cache.store('a1.large',["compose-post-service"])
# results_cache.store('a1.xlarge',["compose-post-service"])