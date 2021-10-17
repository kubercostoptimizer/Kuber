import os
import sys
import json
import logging
import itertools
import csv
sys.path.append('../SSOT')
from conf import ssot
from itertools import combinations
import shutil

class experiment_state:

        def __init__(self):
            self.experiments = dict()
            self.app_folder = ssot.get_app_path()+'/'
            if not os.path.exists(self.app_folder+'/state'):
                  os.mkdir(self.app_folder+'/state')
            if not os.path.exists(self.app_folder+'/result/'):
                  os.mkdir(self.app_folder+'/result/')
            if not os.path.exists(self.app_folder+'/result/data/'):
                  os.mkdir(self.app_folder+'/result/data/')
            self.experiments_file = self.app_folder+'state/experiments.json'
            self.experiment_ids_file = self.app_folder+'state/experiment_ids.json'
            self.result_file = self.app_folder+'/result/result.csv'

            self.init_experiment_state()
            self.first_time = True
        
        def update_experiment_id(self):
                # don't delete when its first element or if no elements
                if len(self.experiment_ids) != 0 and not self.first_time:
                    del self.experiment_ids[0]
                    self.dump_experiment_state()

                if len(self.experiment_ids) == 0:
                     logging.info('[Experiment] experiments are done deleting state')
                     if os.path.exists(self.experiments_file):
                         os.remove(self.experiments_file)
                     if os.path.exists(self.experiment_ids_file):
                         os.remove(self.experiment_ids_file)
                     return False

                self.first_time = False
                self.current_experiment_id = int(self.experiment_ids[0])
                return True
        
        def get_experiment_id(self, service_combination, vm_type):
               for expid,exp in self.experiments.items():
                     if exp[0] == service_combination and exp[1]['name'] == vm_type:
                         return int(expid)
                         
        def save_experiment(self, vm_type, service_combination):
                    #update experiment ids and dump
                    experiment_id = self.get_experiment_id(service_combination,vm_type)
                    if len(self.experiment_ids) != 0:
                         del self.experiment_ids[self.experiment_ids.index(int(experiment_id))]
                         self.dump_experiment_state()

        def set_current_experiment(self, vm_type, service_combination):
                    # check if experiment is already executed
                    self.load_experiment_ids()
                    experiment_id = self.get_experiment_id(service_combination,vm_type)
                    self.current_experiment_id = experiment_id
                    logging.info("[state] setting experiment id to "+str(self.current_experiment_id))
                    return self.current_experiment_id
              
        def get_next_experiment(self):
                # dump experiment id of finished experiment
                if str(self.current_experiment_id) in self.experiments.keys():
                      if not self.update_experiment_id():
                           return None
                      self.init_exp_data()
                      experiment = self.experiments[str(self.current_experiment_id)]
                      logging.info('[Experiment] current experiment ID '+str(self.current_experiment_id))
                      vm_name = experiment[1]['name']
                      services = experiment[0]
                      return vm_name,services
        
        def print_ids(self,service):
                experiment_ids = list()
                with open(self.experiments_file, 'r') as f:
                  self.experiments = json.load(f)
                  for key,data in self.experiments.items():
                         services = data[0]
                         if service in services:
                              experiment_ids.append(key)
                         with open(self.experiment_ids_file, 'w+') as json_file:
                               json.dump(experiment_ids, json_file)
                
        def generate_experiments(self):
                service_combination_id = 1
                number_services = 1
                services = ssot.get_services()
                vms = ssot.get_vm_types()
                for vm in vms:
                   number_services = 1
                   while number_services  <= len(services):
                       for service_comb in combinations(services,number_services):
                         self.experiments[service_combination_id] = [service_comb, vm]
                         service_combination_id = service_combination_id + 1
                       number_services = number_services + 1
                self.dump_experiments()
                self.load_experiments()

        def init_result(self):
             if os.path.exists(self.result_file):
                  os.remove(self.result_file)
             os.mknod(self.result_file)
 
        def init_exp_data(self):
             if os.path.exists(self.app_folder+'/result/data/'+str(self.current_experiment_id)):
                   shutil.rmtree(self.app_folder+'/result/data/'+str(self.current_experiment_id))
             os.mkdir(self.app_folder+'/result/data/'+str(self.current_experiment_id))

        def save_data_files(self,service):
             logging.info('[Experiment] Saving performance '+service+'.json '+self.app_folder+'result/data/'+str(self.current_experiment_id)+'/')
             os.system('mv '+service+'.json '+self.app_folder+'result/data/'+str(self.current_experiment_id)+'/')

        def save_result(self,perf):
             logging.info('[Experiment] Recording performance '+str(perf)+' for experiment '+str(self.current_experiment_id))
             with open(self.result_file, 'a') as csvfile:
                     spamwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                     spamwriter.writerow([self.current_experiment_id,self.experiments[str(self.current_experiment_id)],perf])
             
        def load_experiments(self):
             logging.info('[Experiment] loading experiments from '+self.experiments_file)
             with open(self.experiments_file, 'r') as f:
                  self.experiments = json.load(f)

        def dump_experiments(self):
             logging.info('[Experiment] storing experiments to '+self.experiments_file)
             with open(self.experiments_file, 'w+') as json_file:
                  json.dump(self.experiments, json_file)
        
        def load_experiment_ids(self):
             logging.info('[Experiment] loading experiment ids from '+self.experiment_ids_file)
             with open(self.experiment_ids_file, 'r') as f:
                  self.experiment_ids = json.load(f)

        def load_experiment_state(self):
             logging.info('[Experiment] loading experiment state from '+self.experiment_ids_file)
             with open(self.experiment_ids_file, 'r') as f:
                  self.experiment_ids = json.load(f)
                  if len(self.experiment_ids) > 0:
                       self.current_experiment_id = self.experiment_ids[0]
                  else:
                       self.experiment_ids = range(1, len(self.experiments)) #[str(i) for i in range(1, len(self.experiments))]
                       self.current_experiment_id = 1
                       self.dump_experiment_state()
                  self.first_time = True


        def dump_experiment_state(self):
             logging.info('[Experiment] storing experiment state to '+self.experiment_ids_file)
             with open(self.experiment_ids_file, 'w+') as json_file:
                 json.dump(self.experiment_ids, json_file)

        def init_experiment_state(self):
               logging.info('[Experiment] Initializing experiment state')
               if os.path.exists(self.experiments_file) and os.path.exists(self.experiment_ids_file):
                         self.load_experiments()
                         self.load_experiment_state()
               else:
                         logging.info('[Experiment] no existing experiment state, generating new one!!!')
                         self.generate_experiments()
                         self.experiment_ids = range(1, len(self.experiments)+1) #[str(i) for i in range(1, len(self.experiments))]
                         self.current_experiment_id = 1
                         self.dump_experiment_state()
                         self.init_result()


# root = logging.getLogger()
# root.setLevel(logging.DEBUG)
# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# root.addHandler(handler)

state = experiment_state()
# #state.print_ids('carts')
# print state.current_experiment_id
# print state.get_next_experiment()
# print state.current_experiment_id
# print state.get_next_experiment()
# print state.current_experiment_id
# print state.get_next_experiment()
# print state.current_experiment_id
# state.get_next_experiment()
