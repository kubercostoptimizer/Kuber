import pickle
import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import json
import Jeager_client
import numpy as np
from scipy import stats
import logging
import subprocess
sys.path.append('../SSOT')
from conf import ssot 
sys.path.append('../../../Tools') #for unittest
sys.path.append('../Tools')
from logconf import logconf
import csv

class stats:
      def __init__(self):
            self.result_folder = ssot.get_app_result_folder()
            self.exp_folder = self.result_folder+"/data"
            self.state_folder = ssot.get_app_state_folder()

            self.JC = Jeager_client.Jeager_client()
            self.precision = int(ssot.get_precision())
            self.outliers = int(ssot.get_outliers_removal())
            self.percentile = int(ssot.get_percentile())
            if not os.path.exists(self.state_folder):
                  os.mkdir(self.state_folder)

      def dump_results(self,pickle_file):
            fileObject = open(self.result_folder+pickle_file,'wb') 
            results = self.get_results()
            pickle.dump(results,fileObject)
            fileObject.close()

      def check_errors(self):
            perf_dict = self.get_results()
            for vm_type in ssot.get_vm_types():
                vm_name = vm_type['name']
                if vm_name in perf_dict.keys():
                    for services_p,result_p in perf_dict[vm_name].items():
                        for services_c,result_c in perf_dict[vm_name].items():
                            if set(services_c).issubset(set(services_p)):
                                    if round(result_c[0],1) > round(result_p[0],1):
                                        print result_c[1]," ",result_p[1]," ",services_p," ",result_p[0]," ",services_c," ",result_c[0]," ",vm_name
                                    #else:
                                    #     print "Good"+result_c[1]," ",result_p[1]," ",services_p," ",result_p[0]," ",services_c," ",result_c[0]," ",vm_name
      
      def remove_outliers(self,data):
             if len(data) == 0:
                   return data
             return data[abs(data - np.mean(data)) < self.outliers * np.std(data)] 
 
      def get_exper_data(self,exp_id,service_name):
             from os import path
             if not path.exists(self.exp_folder+'/'+str(exp_id)+'/'+service_name+'.json'):
                   raise Exception('Problem with downloading traces') 

             with open(self.exp_folder+'/'+str(exp_id)+'/'+service_name+'.json') as json_file:
                     data = json.load(json_file)
                     return self.JC.parse_query_json(data['data'],service_name)
      
      def print_stats_for_data(self,data):
             logging.debug("  Number of samples:"+str(len(data)))
             if len(data) == 0:
                 return 0
             Total_samples = len(data)
             logging.info("  Standard dev:"+str(round((1.0*np.std(data)/np.mean(data))*100,self.precision))+"%")
             logging.info("  Mean:"+str(round(np.mean(data)/100000.0,self.precision)))
             logging.info("  90th percentile:"+str(round(np.percentile(data,90)/100000.0,self.precision)))
             logging.info("  ---------------------------------")
             return Total_samples

      def print_stats(self,exp,service_name,operation_name):
             data = np.array(self.get_exper_data(exp,service_name)[operation_name])
             logging.info("*---------------"+str(exp)+"--------------*")
             logging.info("  Number of samples:"+str(len(data)))
             logging.info("  Service name:"+service_name)
             logging.info("  Operator name:"+operation_name)
             logging.info("  ---------------------------------")
             data = self.remove_outliers(data)
             self.print_stats_for_data(data)
             
      def plot_data(self,data):
             mu, std = stats.norm.fit(data)
             plt.hist(data, bins=25, density=True, alpha=0.6)
             xmin, xmax = plt.xlim()
             x = np.linspace(xmin, xmax, 100)
             p = stats.norm.pdf(x, mu, std)
             plt.plot(x, p, 'k', linewidth=2)
             title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
             plt.title(title)
             plt.savefig(exp+'.png')

      def get_perf_data(self,exp,service_name,operation_name):
             data = self.get_exper_data(exp,service_name)[operation_name]
             data = np.array(data)
             data = np.round(data)
             data = self.remove_outliers(data)
             return np.percentile(data,self.percentile)

      def get_data_for_op(self,exp,service_name,operation_name):
             data = self.get_exper_data(exp,service_name)[operation_name]
             return [item for sublist in data for item in sublist]
      
      def get_std(self,exp,service_name,operation_name):
             data = self.get_data_for_op(exp,service_name,operation_name)
             return np.std(data)

      def t_test(self,exp_p,exp_c,service_name,operation_name):
             data_p = self.get_data_for_op(exp_p,service_name,operation_name) 
             perf_p = self.get_perf_data(exp_p,service_name,operation_name)
             data_c = self.get_data_for_op(exp_c,service_name,operation_name) 
             perf_c = self.get_perf_data(exp_c,service_name,operation_name)
             if perf_p < perf_c:
                 logging.debug("parent is better by ",(perf_c-perf_p)/perf_c, perf_c)
             return stats.ttest_ind(data_p,data_c)
      

      def get_performance(self,exp, service_name, percentile):
                perf_data = self.get_exper_data(exp,service_name)
                highest_performance = 0
                for operator_name, perf_list in perf_data.items():
                       arry = self.remove_outliers(np.array(perf_list))
                       if len(arry) == 0:
                              continue
                       pers = np.percentile(arry, percentile)
                       execution_time = round(pers/1000.0,self.precision)
                       if execution_time == 0:
                              continue
                       performance = execution_time
                       if highest_performance < performance:
                            highest_performance = performance
                       logging.info(operator_name+" "+str(percentile)+" percentile "+str(performance)+" secs")
                return highest_performance

      def get_results(self):
                perf_dict = dict()
                with open(self.state_folder+'/experiments.json') as json_file:
                      data = json.load(json_file)
                      with open(self.state_folder+'/experiment_ids.json') as json_file_ids:
                              not_executed_list = json.load(json_file_ids)
                              for exp_id,experiment in data.items():
                                  if int(exp_id) not in not_executed_list:
                                     vm_name = experiment[1]['name']                      
                                     services = experiment[0]
                                     if vm_name not in perf_dict.keys():
                                         perf_dict[vm_name] = dict()
                                     if tuple(services) not in perf_dict[vm_name].keys():
                                         perf_dict[vm_name][tuple(services)] = dict()
                                     for service in services:
                                       try:
                                         perf = self.get_performance(exp_id,service,self.percentile)
                                         if perf < 0:
                                                perf = 0
                                         perf_dict[vm_name][tuple(services)][service] = [perf, exp_id]
                                       except IOError:
                                         #print "Results for service ",service," in experiment ",exp_id," are missing"
                                         continue
                return perf_dict

      def print_service_data(self,exp,service):
                logging.info("*---------------"+str(exp)+"--------------*")
                logging.info("  Service name:"+service)
                data = self.get_exper_data(exp,service)
                for op in data.keys():
                     logging.info("  Operator name:"+op)
                     stats.print_stats_for_data(self.remove_outliers(np.array(data[op])))


def test(exp):
       service = "user-timeline-service"
       stats.print_service_data(exp,service)
       print stats.get_performance(exp,service,stats.percentile)

#logconf.print_console_log()
stats = stats()
# test(5)
#stats.write_performance_to_csv_file("results.csv")

