import os
import sys
import logging
import logging.config
import subprocess
import time
import json
sys.path.append('../../../Infrastructure') #for unittests
sys.path.append('../Infrastructure')
from opennebula import opennebula_client 
import ssh as ssh
from kube import kube_client 
sys.path.append('../../')
from Tools import slack_helper
sys.path.append('../SSOT')
from conf import ssot

class Test_infra:

        def __init__(self):
             self.master_ip = str()
             self.slave_ips = list()
             self.cluster_conf = {
                    "master" : list(),
                    "slaves": list()
                }
             self.number_of_slaves = ssot.get_no_slave_vms()
             self.slave_memory = 4086
             self.slave_cpu = 4
             self.cloud =  opennebula_client()
             self.kube = kube_client()
             self.current_vm_type = list()
             self.witing_time_for_services = 180
             self.cluster_state_folder = 'cluster_state'
             self.dbs = {}
             self.intial_setup_state_file = self.cluster_state_folder + '/inital_setup.json'
             self.current_vm_state_file = self.cluster_state_folder + '/current_vm.json'
             if not os.path.exists(self.cluster_state_folder):
                    os.makedirs(self.cluster_state_folder)


        def delete_test_setup(self):
                self.cloud.delete_master()
                for slave in self.cluster_conf['slaves']:
                        self.cloud.delete_vm(int(slave[1]))
                os.remove(self.intial_setup_state_file)
                os.remove(self.current_vm_state_file)

        def ensure_test_setup(self):
            if os.path.exists(self.intial_setup_state_file):
                self.get_existing_infra(self.intial_setup_state_file)			    
            else:
                self.create_test_infra(self.intial_setup_state_file)
                # sock-shop shortcut remove after issue is fixed
        
        def unicode2String(self,list):
                if list is not None:
                        for idx, val in enumerate(list):
                                list[idx] = str(val)
                        return list

        def get_existing_infra(self, filename):
                    logging.info("[inital setup] reading existing setup config")

                    self.read_infra_config(filename)

                    self.cloud.vaild_master = True
                    self.cloud.masterip = self.cluster_conf['master'][0]
                    self.cloud.mastervmid = int(self.cluster_conf['master'][1])

                    self.kube.reinit(self.cloud.masterip)

                    self.check_cluster_status()
                    
                    logging.info("[inital setup] using existing setup")
                    logging.info("[inital setup] starting the microservice application")
                    
                    self.kube.undeploy(ssot.get_app())
                    self.deploy()
                    
                    self.kube.check_services_up(ssot.get_app(),ssot.get_num_services())

                    return True
            
        def create_test_infra(self,filename):
                self.cluster_conf["master"] = self.cloud.create_master('newton')

                if os.path.exists('../apps/'+ssot.get_app()+'/init_vm.sh'):
                  self.cloud.init_vm(self.cluster_conf["master"][0],'../apps/'+ssot.get_app()+'/init_vm.sh')

                logging.info("[inital setup] creating a new kubernetes master")
        
                slave_ips = list()	
                slave_count = self.number_of_slaves 

                while slave_count>0:
                        slave_ips.append(self.add_vm(4,8,'newton'))
                        slave_count = slave_count - 1
                        if slave_count <= 0:
                                break;
                        slave_ips.append(self.add_vm(4,8,'leibnitz'))
                        slave_count = slave_count - 1
                        if slave_count <= 0:
                                break;
                        slave_ips.append(self.add_vm(4,8,'galileo'))
                        slave_count = slave_count - 1                

                self.cluster_conf['slaves'] = slave_ips
                
                self.check_cluster_status()

                self.write_infra_config(filename)
                    
                logging.info("[inital setup] inital setup done")
                logging.info("[inital setup] starting Istio")
                
                logging.info("[inital setup] starting the microservice application")
                self.deploy()
                
                self.kube.check_services_up(ssot.get_app(),ssot.get_num_services())		

                return True
        
        def is_current_node_up(self):
                if self.kube.get_status_node(self.current_vm_type[2]) != "True":
                        return False
                return True

        def make_test_vmtype(self,vm_type):
             self.read_current_vm_type(self.current_vm_state_file)
             if self.current_vm_type == list() or vm_type != self.current_vm_type[0]:
                self.delete_current_VM() #if exists and needs to be changed
                self.current_vm_type = list()
                self.current_vm_type.append(vm_type)
                logging.info("[experiment setup] creating vm type "+vm_type)
                vm_data = self.cloud.add_slave(vm_type)
                vm = list(vm_data)
                self.current_vm_type.append(vm_data)
                self.current_vm_type.append(self.cloud.get_hostname(self.current_vm_type[1][0]))
                logging.info("[experiment setup] vm type "+vm_type+" is created at "+self.current_vm_type[1][0])
                self.write_current_vm_type(self.current_vm_state_file)
                time.sleep(30)
                logging.info('[sleep] 30 for new VM type')
                if os.path.exists('/wd/code/apps/'+ssot.get_app()+'/init_vm.sh'):
                        self.cloud.init_vm(vm[0],'/wd/code/apps/'+ssot.get_app()+'/init_vm.sh')
             else:
                self.kube.drain_test_machines(self.current_vm_type[2],ssot.get_app())
             return self.current_vm_type


        def delete_current_VM(self):
                if self.current_vm_type != list():
                    logging.info("[experiment setup] delete vm type "+self.current_vm_type[1][0])
                    self.delete_vmtype(self.current_vm_type[1][1],self.current_vm_type[1][0])
                    self.current_vm_type = list()
                    os.remove(self.current_vm_state_file)


        def expose_app(self):
                self.kube.expose_front_end(ssot.get_app(),ssot.get_front_end(),ssot.get_port())

        def deploy(self):
                self.kube.init_register_docker_credentials()
                self.kube.init_istio()
                self.kube.init_metrics()
                self.kube.deploy(ssot.get_app())
                logging.info('[sleep] '+str(self.witing_time_for_services))
                time.sleep(self.witing_time_for_services)
                self.expose_app()
                print ssot.get_app()
                if os.path.exists('/wd/code/apps/'+ssot.get_app()+'/'+'load_test/init_scripts/run.sh'):
                     subprocess.call(['sh '+'/wd/code/apps/'+ssot.get_app()+'/'+'load_test/init_scripts/run.sh'], shell=True)
                self.check_app_works()
             
        
        def redeploy(self):
                self.kube.undeploy(ssot.get_app())
                self.deploy()
        
        def restart_service(self,service):
                self.kube.restart_service(service,ssot.get_app())
                time.sleep(30)

        def deploy_to_test_vmtype(self,services):
              self.kube.init_Jeager()
              #self.kube.init_metrics()
              for service in services:
                      self.kube.assain_service_to_testVM(self.current_vm_type[2],service,ssot.get_app())
                      if service in self.dbs.keys():
                           self.kube.assain_service_to_testVM(self.current_vm_type[2],self.dbs[service],ssot.get_app())
              logging.info('[sleep] '+str(self.witing_time_for_services))
              time.sleep(self.witing_time_for_services-50)

        def undeploy_to_test_vmtype(self,services):
              for service in services:
                      self.kube.remove_service_from_testVM(self.current_vm_type[2],service,ssot.get_app())

        def get_ip_loadtest(self):
               # 1.get the port from the config file
               #return self.cloud.masterip + ":" + ssot.get_port()
               return "127.0.0.1"

        def check_app_works(self):
                logging.info("[check] checking "+ssot.get_app()+" application API")
                host = self.get_ip_loadtest()
                sys.path.append('/wd/code/apps/'+ssot.get_app())
                import app
                if app.check(host,ssot.get_port()):
                    logging.info("[check passed] "+ssot.get_app()+" API is working")
                else:
                    logging.error("[check failed] "+ssot.get_app()+" API is not working")
                    raise  ValueError('Application API is not UP')

        def delete_vmtype(self,vm_id,vm_ip):
                self.cloud.delete_vm(vm_id)
                self.kube.delete_node("onekube-ip-" + vm_ip.replace(".", "-") + ".localdomain")

        def add_vm(self,CPU,memory,machine):
              logging.info("[experiment setup] adding new machines with "+str(CPU)+" "+str(memory)+" "+str(machine))
              vm = list(self.cloud.add_coustom_slave(CPU,memory,machine))
              if os.path.exists('../apps/'+ssot.get_app()+'/init_vm.sh'):
                  self.cloud.init_vm(vm[0],'../apps/'+ssot.get_app()+'/init_vm.sh')
              return vm
              
        def read_infra_config(self,filename):
             try:
               with open(filename, 'r') as f:
                    cluster_conf = json.load(f)
                    self.cluster_conf['master'].append(cluster_conf['master'][0])
                    self.cluster_conf['master'].append(cluster_conf['master'][1])
                    for slave_ip in cluster_conf['slaves']: 
                         self.cluster_conf['slaves'].append([str(slave_ip[0]),str(slave_ip[1])])
             except:
               logging.error('error reading from File '+filename) 

        def write_infra_config(self,filename):
               with open(filename, 'w') as json_file:
                    json.dump(self.cluster_conf, json_file)
        
        def read_current_vm_type(self,filename):
                if os.path.exists(filename):
                        try:
                                with open(filename, 'r') as f:
                                        current_vm_type = json.load(f)
                                        self.current_vm_type = list()
                                        self.current_vm_type.append(str(current_vm_type[0]))
                                        self.current_vm_type.append(list())
                                        self.current_vm_type[1].append(str(current_vm_type[1][0]))
                                        self.current_vm_type[1].append(current_vm_type[1][1])
                                        self.current_vm_type.append(str(current_vm_type[2]))
                        except Exception as e:
                                logging.error(e)
                                logging.error('error reading from File '+filename)
                

        def write_current_vm_type(self,filename):
                with open(filename, 'w') as json_file: 
                      json.dump(self.current_vm_type, json_file)  
                          
        def check_cluster_status(self):
            logging.info("[check] checking kubernetes slaves and master")
            self.kube.check_wait("onekube-ip-" +self.cluster_conf['master'][0].replace(".", "-") + ".localdomain")
            for slave_ip in self.cluster_conf['slaves']:
                  self.kube.check_wait("onekube-ip-" + slave_ip[0].replace(".", "-") + ".localdomain")
            logging.info("[check passed] kubernetes slaves and master working")


# _infra.ensure_test_setup()
#_infra.kube.deploy('sock-shop')
#_infra.cluster_conf['master_ip'] = '192.168.122.23'
#_infra.kube.reinit(_infra.cluster_conf['master_ip'])
#_infra.check_cluster_status()
infra = Test_infra()

# infra.read_infra_config(infra.intial_setup_state_file)

# infra.cloud.vaild_master = True
# infra.cloud.masterip = infra.cluster_conf['master'][0]
# infra.cloud.mastervmid = int(infra.cluster_conf['master'][1])

# infra.kube.reinit(infra.cloud.masterip)   
# infra.kube.init_metrics()     
# _ , vm, host_name = infra.make_test_vmtype('t3.micro')
# from results_cache import results_cache
# results_cache.store_metrics(1,infra.kube.get_metrics_instance_name(host_name),'t3.micro',"('url-shorten-service')")

# print infra.kube.get_metrics_instance_name('onekube-ip-192-168-122-26.localdomain')
#infra.read_current_vm_type('data/current.json')
#print infra.current_vm_type
