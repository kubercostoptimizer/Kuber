import time
import logging
import subprocess
import sys
import os
from kubernetes import client, config, watch
sys.path.append('../../')
from Tools import slack_helper
homepath = "/root"
apps_dir = "../apps"

docker_password = os.environ['DOCKERPASS'] 
docker_username = os.environ['DOCKERID'] 
docker_mail = os.environ['DOCKERMAIL'] 

class kube_client:

    def reinit(self,masterip):
            global v1
            global extensions_v1beta1
            self.get_kube_conf(masterip)
            config.load_kube_config()
            extensions_v1beta1 = client.ExtensionsV1beta1Api()
            v1 = client.CoreV1Api()
            subprocess.call(['pkill kubectl'], shell=True)
            logging.info('[sleep] '+str(10))

    def read_node_resources(self,namespace):
         api = client.CustomObjectsApi(config)
         resource = api.list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1", namespace=namespace, plural="nodes")
         for node in resource["items"]:
             print(node, "\n")

    def get_machine_with_tag(self,key,value):
            node_list = []
            for node in v1.list_node().items:
               if key in node.metadata.labels:
                 logging.info(str(node.metadata.labels[key])+' '+str(value))
                 if node.metadata.labels[key] == value:
                   node_list.append(node.metadata.name)
            return node_list

    def get_status_node(self,node_name):
            for node in v1.list_node().items:
                if node.metadata.labels["kubernetes.io/hostname"] == node_name:
                    for condition in node.status.conditions:
                        if condition.type == "Ready":
                            return condition.status

    def get_deployment(self,service,namespace):
         deployments_list = extensions_v1beta1.list_namespaced_deployment(namespace)
         if deployments_list is None:
             return
         for deployment in deployments_list.items:
              if deployment.metadata.name == service:
                 return deployment

    def drain_test_machines(self,hostname,namespace):
         nodes = self.get_machine_with_tag("kubernetes.io/hostname",hostname)
         for node in nodes:
             field_selector = 'spec.nodeName='+node
             ret = v1.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
             for pod in ret.items:
                 if pod.metadata.namespace == namespace:
                    if 'app-name' in pod.metadata.labels:
                        self.remove_service_from_testVM(hostname,pod.metadata.labels['app-name'],pod.metadata.namespace)
                    elif 'io.kompose.service' in pod.metadata.labels:
                        self.remove_service_from_testVM(hostname,pod.metadata.labels['io.kompose.service'],pod.metadata.namespace)
                        

    def check_wait(self,node_name):
            start_time = time.time()
            flag = False
            while self.get_status_node(node_name) != "True":
                running_time = time.time() - start_time
                if running_time > 60 and not flag :
                    # TODO send message
                    slack_helper.send_message("wait node  " + node_name + " failed")
                    slack_helper.send_message("check")
                    flag = True
                    pass
                pass

    def attach_services_to_vm_type(services_list, namespace, hostname):
        check_wait(hostname)
        logging.info("wait done")
        for service in services_list:
            assain_service_to_testVM(hostname, service, namespace)


    def get_node_selector_obj(self,nodelist,flag,service,namespace):

            deployment = self.get_deployment(service,namespace)

            # add required tolerations
            toleration = client.models.v1_toleration.V1Toleration()
            toleration.effect = "NoSchedule"
            toleration.key = "dedicated"
            toleration.value = "test"
            toleration.operator = "Equal"
            affinity_str = ""
            if flag == True:
              affinity_str = "In"
            else:
              affinity_str = "NotIn"

            # add required node affinities
            node_selector_terms  = client.models.v1_node_selector_term.V1NodeSelectorTerm()
            node_selector_terms.match_expressions = [client.models.v1_node_selector_requirement.V1NodeSelectorRequirement('kubernetes.io/hostname',affinity_str,[])]
            required_during_scheduling_ignored_during_execution = client.models.v1_node_selector.V1NodeSelector([node_selector_terms])
            required_during_scheduling_ignored_during_execution.node_selector_terms = [node_selector_terms]
            affinity = client.models.v1_node_affinity.V1NodeAffinity()
            affinity.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

            # update the spec
            deployment.spec.template.spec.affinity = client.models.v1_affinity.V1Affinity()
            deployment.spec.template.spec.affinity.node_affinity = affinity
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].key = 'kubernetes.io/hostname'
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].operator = affinity_str
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].values = nodelist
            deployment.spec.template.spec.tolerations = [toleration]

            return deployment

    def assain_service_to_testVM(self,hostname,service,namespace):

            #import time
            #start_time = time.time()
            #print("--- %s seconds ---" % (time.time() - start_time))

            service = str(service)
            time.sleep(10)
            Test_node_name = self.get_machine_with_tag("kubernetes.io/hostname",hostname)
            logging.info(str(hostname)+' '+str(Test_node_name))
            logging.info("[experiment] Moving the service "+service+" to the node "+str(Test_node_name))

            deployment = self.get_node_selector_obj(Test_node_name,True,service,namespace)

            # Update the spec
            # Retry for 5 times if conflit exception happens due to quick change in resources
            count = 0
            while True:
             try:
                 api_response = extensions_v1beta1.patch_namespaced_deployment(
                    name=service,
                    namespace=namespace,
                    body=deployment)
             except Exception as e:
                  deployment = self.get_node_selector_obj(Test_node_name,True,service,namespace)
                  if deployment is None:
                      return
                  if count > 30:
                      break
                  count = count + 1
                  time.sleep(5)
             break


    def remove_service_from_testVM(self,hostname,service,namespace):

            if service == "":
              return
            deployment = self.get_deployment(service,namespace)

            Test_node_name = self.get_machine_with_tag("kubernetes.io/hostname",hostname)

            logging.info("[experiment] Removing the service "+str(service)+" from node "+str(Test_node_name))

            deployment = self.get_node_selector_obj(Test_node_name,False,service,namespace)
            deployment.spec.template.spec.tolerations = []

            # Update the spec
            # Retry for 5 times if conflit exception happens due to quick change in resources
            count = 0
            while True:
             try:
                 api_response = extensions_v1beta1.patch_namespaced_deployment(
                    name=service,
                    namespace=namespace,
                    body=deployment)
             except Exception as e:
                  deployment = self.get_node_selector_obj(Test_node_name,False,service,namespace)
                  deployment.spec.template.spec.tolerations = []
                  if deployment is None:
                      return
                  if count > 30:
                      break
                  count = count + 1
                  time.sleep(5)
             break
    
    def get_kube_conf(self,ip):
            subprocess.call(['ssh-keygen -f "' + homepath + '/.ssh/known_hosts" -R ' + ip], shell=True)
            subprocess.call(['scp root@' + ip + ':/etc/kubernetes/admin.conf ' + homepath + '/.kube/config'], shell=True)

    def expose_front_end(self,app,frontendsvc,port):
            logging.info('[experiment] exposing front-end '+frontendsvc)
            if port != 16686:
                subprocess.call(['kubectl -n '+app+' port-forward svc/'+frontendsvc+' '+str(port)+':'+str(port)+' &'], shell=True)
            time.sleep(2)

    def deploy(self,app):
        try:
            logging.info('[experiment] deploying app '+app)
            subprocess.call(['kubectl create namespace '+ app], shell=True)
            time.sleep(2)
            subprocess.call(['kubectl -n '+app+' create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username='+docker_username+' --docker-password='+docker_password+' --docker-email='+docker_mail], shell=True)
            subprocess.call(['kubectl label namespace '+app+' istio-injection=enabled'], shell=True)
            subprocess.call(['kubectl -n '+app+' create -f '+apps_dir+'/'+app+'/deploy/'], shell=True)
            time.sleep(5)
            #subprocess.call(['kubectl -n '+app+' replace -f '+apps_dir+'/'+app+'/rate_limits/'], shell=True)
        except Exception as e:
            logging.error(e)
        
    def delete_node(self,node):
        logging.info('[experiment] deleting node '+node)
        subprocess.call(['kubectl delete node '+node], shell=True)
        time.sleep(2)

    def undeploy(self,app):
        logging.info('[experiment] undeploying app '+app)
        subprocess.call(['kubectl -n '+app+' delete -f '+apps_dir+'/'+app+'/deploy/'], shell=True)
        time.sleep(5)

    def check_services_up(self,app,num_services):

        logging.info("[check] checking all services are up")
        try:
            try_services_count = 600
            while try_services_count != 0:        
                    if subprocess.check_output("kubectl -n "+app+" get deployments | awk '{print $2}' | tail -n "+str(num_services)+" | grep -c '1/1'", shell=True) == str(num_services)+'\n':
                        break
                    time.sleep(5)
                    try_services_count = try_services_count-1
            if try_services_count == 0:
                exit()
        except:
            logging.info("[check failed] none of the services are up ")
            slack_helper.send_message("none of the services are up")
            raise Exception("[check failed] none of the services are up")
        logging.info("[check passed] all services are up")
    
    def scale_deployment(self,deployment,namespace,number):
            subprocess.call(['kubectl -n '+namespace+' scale deployments/'+deployment+' --replicas='+str(number)], shell=True)

    def init_istio(self):
            subprocess.call(['istioctl install -f ../data/istio-ext.yaml'], shell=True)
            subprocess.call(['istioctl manifest apply --set profile=demo'], shell=True)
            time.sleep(10)
            self.init_Jeager()
    
    def init_register_docker_credentials(self):
            subprocess.call(['kubectl -n monitoring create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username='+docker_username+' --docker-password='+docker_password+' --docker-email='+docker_mail], shell=True)

    def init_metrics(self):
            subprocess.call(['kubectl create namespace monitoring'], shell=True)
            subprocess.call(['kubectl delete -f /wd/code/Infrastructure/data/metrics.yaml'], shell=True)
            time.sleep(10)
            subprocess.call(['kubectl create -f /wd/code/Infrastructure/data/metrics.yaml'], shell=True)
            time.sleep(10)


    def restart_service(self,service,app):
            self.scale_deployment(service,app,0)
            logging.info('[sleep] '+str(10))
            time.sleep(10)
            self.scale_deployment(service,app,1)
            logging.info('[sleep] '+str(30))

    def init_Jeager(self):
            self.scale_deployment('istio-tracing','istio-system',0)
            logging.info('[sleep] '+str(10))
            time.sleep(10)
            self.scale_deployment('istio-tracing','istio-system',1)
            logging.info('[sleep] '+str(30))
            time.sleep(30)  
            subprocess.call(['pkill kubectl'], shell=True)
            logging.info('[sleep] '+str(10))
            time.sleep(10)
            subprocess.call(['kubectl port-forward -n istio-system svc/jaeger-query 16686:16686&'], shell=True)
            subprocess.call(['kubectl port-forward -n monitoring svc/prometheus-service 15678:15678&'], shell=True)
    
    def get_metrics_instance_name(self,node):
        pod_list = v1.list_namespaced_pod("monitoring")
        for pod in pod_list.items:
           if node == pod.spec.node_name:
               return pod.status.pod_ip
    