import logging
import subprocess
import time
import os
import struct
import signal
import sys
import re
import time
import json
import numpy as np
import pyone
import paramiko
sys.path.append('../SSOT')
from conf import ssot 
sys.path.append('../../../') #for unittest
sys.path.append('../')
from Tools import slack_helper
from ssh import ssh_client
from kube import kube_client

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
dir_path = os.path.dirname(os.path.abspath(__file__))

password = os.environ['PASSWORD'] 
username = os.environ['USERNAME'] 
user_id  = int(os.environ['USERID'])
publickeyPath = "/root/.ssh/id_rsa.pub"
templateId    = 1

class opennebula_client:

        def __init__(self):
               self.vaild_master = False
               self.mastervmid = -1
               self.masterip = str()
               self.masterHash = str()
               self.masterToken = str()
               self.kube = kube_client() 
               self.machine_ids = dict()
               self.machine_ids['newton'] = 1
               self.machine_ids['leibnitz'] = 2
               self.machine_ids['galileo'] = 3

        def check_physical_machines(self):

            logging.info("[check] checking physical machines")

            try:
                subprocess.check_output(["sshpass -p "+password+" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+username+"@10.32.33.18 ls"], shell=True)
            except subprocess.CalledProcessError as e:
                slack_helper.send_message("leibnitz not working")
                logging.error("[check failed] leibnitz not working")

            try:
                subprocess.check_output(["sshpass -p "+password+" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+username+"@10.32.33.17 ls"], shell=True)
            except subprocess.CalledProcessError as e:
                slack_helper.send_message("darwin not working")
                logging.error("[check failed] darwin not working")

            try:
                subprocess.check_output(["sshpass -p "+password+" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+username+"@10.32.33.20 ls"], shell=True)
            except subprocess.CalledProcessError as e:
                slack_helper.send_message("galileo not working")
                logging.error("[check failed] galileo not working")

            try:
                subprocess.check_output(["sshpass -p "+password+" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "+username+"@10.32.33.19 ls"], shell=True)
            except subprocess.CalledProcessError as e:
                slack_helper.send_message("galileo not working")
                logging.error("[check failed] galileo not working")

            logging.info("[check passed] all physical machines are up")

        def have_enough_space(self,vm_type):
                one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
                cpu_count = np.fromstring(ssot.get_vm_attr(vm_type)[0], dtype=int, sep=' ')[0]
                ram = np.fromstring(ssot.get_vm_attr(vm_type)[1], dtype=float, sep=' ')[0]
                speed = ssot.get_vm_attr(vm_type)[2]
                machine = ssot.get_vm_attr(vm_type)[3]

                print machine
                host = one.hostpool.info().HOST[self.machine_ids[machine]]
                print host.HOST_SHARE.get_MEM_USAGE()/100000
                print host.HOST_SHARE.get_FREE_CPU()
                print  host.HOST_SHARE.get_FREE_DISK()
                
                #if host.HOST_SHARE.get_FREE_MEM() > ram and host.HOST_SHARE.get_FREE_CPU() > cpu_count and host.HOST_SHARE.get_FREE_DISK() > 100:
                return False

        def add_slave(self,vm_type): 

            if not self.vaild_master:
                logging.error('no valid kubernetes master')
                return

            self.update_public_key()


            self.masterToken   = self.ssh_get_parameter(self.masterip, "k8s_token")
            self.masterHash    = self.ssh_get_parameter(self.masterip, "k8s_hash")

 
            # Get vm type attributes from config 
            cpu_count = np.fromstring(ssot.get_vm_attr(vm_type)[0], dtype=int, sep=' ')[0]
            ram = np.fromstring(ssot.get_vm_attr(vm_type)[1], dtype=float, sep=' ')[0]
            speed = ssot.get_vm_attr(vm_type)[2]
            machine = ssot.get_vm_attr(vm_type)[3]

 
            logging.info('starting a new vm type '+str(vm_type))
            one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
            memory = 1024 * ram

            vm_id = one.template.instantiate(templateId, 'kube_slave '+vm_type, False, {
            'TEMPLATE': {
                'SCHED_REQUIREMENTS': 'ID=\"' + str(self.machine_ids[machine]) + '\"',
                'MEMORY'            : str(int(memory)),
                'VCPU'              : str(cpu_count),
                'CPU'               : str(cpu_count),
                'NIC'               : {
                'NETWORK': 'ReSeSS',
                'NETWORK_ID': '0',
                'NIC_ID': '0',
                },
                'ONEAPP_K8S_ADDRESS': self.masterip,
                'ONEAPP_K8S_HASH': self.masterHash,
                'ONEAPP_K8S_TOKEN': self.masterToken,
                'ONEGATE_ENABLE': "YES",
            }}, False)
            
            ip = str(one.vm.info(vm_id).TEMPLATE['CONTEXT']['ETH0_IP'])

            self.wait_machine(ip)
            
            return ip, vm_id
        
        def update_public_key(self):
            # get public key from local
            f = open(publickeyPath, "a+")
            publickey =  f.readline().strip()
            # 2. update the user's public key
            one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
            one.user.update(user_id, {
            'TEMPLATE': {
                'SSH_PUBLIC_KEY': publickey,
            }}, 1)
            logging.info('line')

        def create_master(self,machine):

            logging.info("[create_master] create master")

            self.update_public_key()

            one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
            
            # 3. create master
            self.mastervmid = one.template.instantiate(templateId, "kube_master", False, {
            'TEMPLATE': {
                'SCHED_REQUIREMENTS': 'ID=\"' + str(self.machine_ids[machine]) + '\"',
                'MEMORY': str(int(8096)),
                'VCPU': str(8),
                'CPU': str(8),
                'NIC': {
                'NETWORK': 'ReSeSS',
                'NETWORK_ID': '0',
                'NIC_ID': '0',
                },
                'ONEGATE_ENABLE': "YES",
            }}, False)
            
            # 4. wait
            logging.info("[create_master] create master done, start to wait")
            self.masterip = str(one.vm.info(self.mastervmid).TEMPLATE['CONTEXT']['ETH0_IP'])
            self.wait_machine(self.masterip)
            
            # 5. get token, hash, ip
            self.masterToken   = self.ssh_get_parameter(self.masterip, "k8s_token")
            self.masterHash    = self.ssh_get_parameter(self.masterip, "k8s_hash")
            
            # reload config
            self.kube.reinit(self.masterip)

            self.vaild_master = True
    
            #reate default slaves
            return self.masterip,self.mastervmid

        def delete_master(self):
             self.delete_vm(self.mastervmid)

        def add_coustom_slave(self,CPU,memory, machine):
                if not self.vaild_master:
                    logging.error('no valid kubernetes master')
                    return
                
                self.update_public_key()

                self.masterToken   = self.ssh_get_parameter(self.masterip, "k8s_token")
                self.masterHash    = self.ssh_get_parameter(self.masterip, "k8s_hash")

                one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
                memory = 1024 * memory
                _id = one.template.instantiate(templateId, "slave", False, {
                'TEMPLATE': {
                    'SCHED_REQUIREMENTS': 'ID=\"' + str(self.machine_ids[machine]) + '\"',
                    'MEMORY'            : str(int(memory)),
                    'VCPU'              : str(CPU),
                    'CPU'               : str(CPU),
                    'NIC'               : {
                    'NETWORK': 'ReSeSS',
                    'NETWORK_ID': '0',
                    'NIC_ID': '0',
                    },
                    'ONEAPP_K8S_ADDRESS': self.masterip,
                    'ONEAPP_K8S_HASH': self.masterHash,
                    'ONEAPP_K8S_TOKEN': self.masterToken,
                    'ONEGATE_ENABLE': "YES",
                }}, False)
                ip_slave = str(one.vm.info(_id).TEMPLATE['CONTEXT']['ETH0_IP'])
                
                self.wait_machine(ip_slave)
                
                return ip_slave, _id

        def wait_machine(self,ip):

                # Are we able to ssh into machine ?
                count = 150
                while count > 0:
                    try:
                        sshclient = paramiko.SSHClient()
                        sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        sshclient.connect(ip, username='root', password='foo')
                        break
                    except Exception as e:
                        print e
                        time.sleep(1)
                        count = count - 1
                        os.system("scp "+dir_path+"/data/sshd_config "+ip+":/etc/ssh/sshd_config")
                        os.system("ssh "+ip+" 'service sshd restart'")
                        logging.info("[check trying] machine not ready, wating .. remain" + str(count) + " to try")

                    if count == 0:
                        raise Exception("master not ready")
                        exit()

                logging.info("[check result] "+ip+" VM is responding for ssh")
                logging.info("[check] checking kubernetes node status")

                # is machine connected to kubernetes master?
                status_count = 600
                while status_count > 0:
                    sshclient = paramiko.SSHClient()
                    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    sshclient.connect(ip, username='root', password='foo')
                    stdin, stdout, stderr = sshclient.exec_command("cat /etc/one-appliance/status")
                    status = ''
                    for line in iter(stdout.readline, ""):
                        if line is not "":
                            status = line
                    if "bootstrap_success" in status:
                        logging.info("[check] kubernetes node is up")
                        break
                    status_count = status_count - 1
                    time.sleep(1)
                    if status_count == 0:
                        raise Exception("machine" + ip + "failed to start")

        def init_vm(self,ip,inti_script):
                sshclient = paramiko.SSHClient()
                sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sshclient.connect(ip, username='root', password='foo')
                ftp_client = sshclient.open_sftp()
                ftp_client.put(inti_script,'init.sh')
                ftp_client.close()
                sshclient.exec_command('sh init.sh')

        def ssh_get_parameter(self, ip, param_name):
                sshclient = paramiko.SSHClient()
                sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sshclient.connect(ip, username='root', password='foo')
                stdin, stdout, stderr = sshclient.exec_command("awk -F '=' '/" + param_name + "/ {print $2}' /etc/one-appliance/config")
                param = ''
                for line in iter(stdout.readline, ""):
                    if line is not "":
                        param = line
                    param = param.replace("\r", "")
                    param = param.replace("\n", "")
                    param = param.replace(" ", "")
                return param

        def delete_vm(self, vm_id):
                one = pyone.OneServer("http://10.32.33.17:2633/RPC2", session=username+":"+password)
                return one.vm.action('terminate', int(vm_id))

        def getVMstatus(self, vmId):
                # high risk code clean it up soon
                clusterMasterIp = "10.32.33.17" # darwin's IP

                sshclient = paramiko.SSHClient()
                sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                sshclient.connect(clusterMasterIp, username=username, password=password)
                stdin, stdout, stderr = sshclient.exec_command("onevm list | grep " + vmId +" | awk {'print $5'}")
                exit_status = stdout.channel.recv_exit_status()  # Blocking call
                if exit_status == 0:
                    logging.info("done execute the get status command")
                else:
                    logging.error("Error", exit_status)

                result = []
                for line in iter(stdout.readline, ""):
                    result.append(line)
                return result[len(result) - 1]

        def isRunning(self, vmId):
                if "runn" in getVMstatus(vmId):
                    return True
                else:
                    return False
        def get_hostname(self,vm_ip):
                return "onekube-ip-" + vm_ip.replace(".", "-") + ".localdomain"

# # Tests
# oc = opennebula_client()
# #oc.create_master()
# #oc.add_slave('c4.large')
# oc.delete_vm(565)
