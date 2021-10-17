import requests
import decimal
import subprocess
import time
import logging

class Metrics_client:
    def __init__(self):
            self.prometheus_address = 'http://localhost:15678/'

    def run_query(self,query):
            params = {}
            params['query'] = query
            response =requests.get(self.prometheus_address + '/api/v1/query', params=params) 
            if response.status_code == 200:
                json_data = response.json()
                return json_data['data']['result']
            else:
                return None
    
    def get_node_names(self):
            query = 'up'
            data = self.run_query(query)
            for item in data:
                print item


    def get_data_for_query(self,host_ip,duration):
            cpus_idle = []
            cpus_user = []
            cpus_sys = []
            pysical_mem = 0
            cache = 0
            buffer = 0
            procs_running = 0
            procs_blocked = 0
            load1 = 0
            load5 = 0
            load15 = 0
            
            subprocess.call(['pkill kubectl'], shell=True)
            logging.info('[sleep] killed kubectl'+str(10))
            time.sleep(10)
            subprocess.call(['kubectl port-forward -n monitoring svc/prometheus-service 15678:15678&'], shell=True)
            logging.info('[sleep] port forward on 15678 for metric server'+str(10))
            time.sleep(10)
            # exit()

            D = decimal.Decimal
            query = 'avg_over_time(node_cpu_seconds_total{mode="idle",instance="'+host_ip+':9100"}['+duration+'])'
            # query = 'node_cpu_seconds_total'
            data = self.run_query(query)
            if data is not None:
                for item in data:
                    cpus_idle.append(D(item['value'][1]))
                cpu_idle_mean = round(sum(cpus_idle)/len(cpus_idle),2)
            else:
                print "CPU idle metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_cpu_seconds_total{mode="user",instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                for item in data:
                    cpus_user.append(D(item['value'][1]))
                cpu_user_mean = round(sum(cpus_user)/len(cpus_user),2)
            else:
                print "CPU user metrics not available"
            

            D = decimal.Decimal
            query = 'avg_over_time(node_cpu_seconds_total{mode="system",instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                for item in data:
                    cpus_sys.append(D(item['value'][1]))
                cpu_sys_mean = round(sum(cpus_sys)/len(cpus_sys),2)
            else:
                print "CPU sys metrics not available"
            
            D = decimal.Decimal
            query = 'avg_over_time(node_memory_MemAvailable_bytes{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                pysical_mem = round(D(item['value'][1]),2)
            else:
                print "Available memory metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_memory_Cached_bytes{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                cache = round(D(item['value'][1]),2)
            else:
                print "Cache metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_memory_Buffers_bytes{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                buffer = round(D(item['value'][1]),2)
            else:
                print "Buffer metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_procs_blocked{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                procs_blocked = round(D(item['value'][1]),2)
            else:
                print "Number of process blocked metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_procs_running{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                procs_running = round(D(item['value'][1]),2)
            else:
                print "Number of process running metrics not available"

            D = decimal.Decimal
            query = 'avg_over_time(node_load1{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                load1 = round(D(item['value'][1]),2)
            else:
                print "load 1m metrics not available"


            D = decimal.Decimal
            query = 'avg_over_time(node_load5{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                load5 = round(D(item['value'][1]),2)
            else:
                print "load 5m metrics not available"


            D = decimal.Decimal
            query = 'avg_over_time(node_load5{instance="'+host_ip+':9100"}['+duration+'])'
            data = self.run_query(query)
            if data is not None:
                item = data[0]
                load15 = round(D(item['value'][1]),2)
            else:
                print "load 15m metrics not available"

            return cpu_idle_mean,cpu_user_mean,cpu_sys_mean,pysical_mem,cache,buffer,procs_running,procs_blocked,load1,load5,load15

#print Metrics_client().get_node_names()
#print Metrics_client().get_data_for_query('10.244.1.92','2m')
# print Metrics_client().get_data_for_query('10.244.3.175','2m')
# print Metrics_client().get_data_for_query('10.244.2.76','2m')
# print Metrics_client().get_data_for_query('10.244.124.52','2m')
# print Metrics_client().get_data_for_query('10.244.1.78','2m')