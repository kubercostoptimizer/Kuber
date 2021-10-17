import sys
import os 
import math
import numpy as np
import requests
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
import logging
#matplotlib.use('Agg')
import EoN
sys.path.append('../SSOT')
from conf import ssot
import subprocess
import time

# Jeager_UI_client uses a Json to communicate with Jeager_query service
# In this class, we parse this Json to get percentile performance for a service between a start and end time
class Jeager_client:
        
        def __init__(self):
                self.Jeager_host = "localhost"
                self.Jeager_address = "http://"+self.Jeager_host+":16686/jaeger/api/traces"
        
        # Intent: To create a lookup table with service names as keys and process ids as data
        # Assumptions:
        # The structure of process_json 
        # process_id_1 : 
        #    serviceName: name
        # process_id_2:
        #    serviceName: name
        def parse_process_json(self, process_json):
              process_names = dict()
              for process_id,data in process_json.items():
                    process_names[data['serviceName']] = process_id
              return process_names
          
        # Context: Each trace has many spans and each span is one execution instance and represents a method.
        # Intent: 
        # 1. For each execution, we are need to know service name, operation name, and execution time.
        # 2. Parent operator has calls to multiple child operators, to get parents execution time
        # 3. We reduce parent execution time by child's execution time.
        # 4. We check errors at system level (at front ends) and ignore at each service level.
        # Assumptions: 
        # 1. Structure of span_json
        # spans:
        #    0:
        #      spanID:
        #      operationName
        #      duration:
        #    1:
        #      spanID:
        #      operationName
        #      duration:
        # 2. Relations between spans are specified by references. 
        # We made assumption that if operationa CHILD_OF operationb
        # operationb called operationa. So we substracted 
        # references:
        #   0:
        #    refType:
        #    spanID:
        def parse_span_json(self, span_json, process_id):
              span_dict = dict()
              G = nx.DiGraph()
              for span in span_json:
                   if span['operationName'] != 'error':
                       span_dict[span['spanID']] = [0,list()]
                       span_dict[span['spanID']][0] = int(span['duration'])
                       span_dict[span['spanID']][1].append(span['processID']) 
                       span_dict[span['spanID']][1].append(span['operationName'])
                       for reference in span['references']:
                             if reference['refType'] == 'CHILD_OF':
                                     G.add_edge(reference['spanID'],span['spanID'])
                   else:
                       logging.info("Their is error in operation ",span['operationName'])
              
              G1 = G.copy()
              for node in G.nodes():
                 if node not in span_dict.keys():
                      G1.remove_node(node)
              G = G1
              # Get count of parent nodes
              top_nodes = list()
              for node in G.nodes():
                    if node in span_dict.keys() and span_dict[node][1][0] == process_id:
                         top_nodes.append(node)

              for node in top_nodes:              
                        parent = node
                        children = list(G.successors(parent))
                        for child in children:
                                if parent in span_dict.keys() and child in span_dict.keys():
                                        logging.debug('parent '+span_dict[parent][1][1]+' exe time '+str(span_dict[parent][0]))
                                        logging.debug('child '+span_dict[child][1][1]+' exe time '+str(span_dict[child][0]))
                                        temp = span_dict[parent][0]
                                        span_dict[parent][0] = span_dict[parent][0] - span_dict[child][0]
                                        # if sum of runtime of all children is grater than paerent then we will nagitive values for parent
                                        # this can happen if a child span is opened and forgot to close.
                                        # in such cases we will retain parent value just before becoming nagitive.
                                        if span_dict[parent][0] < 0:
                                            span_dict[parent][0] = temp
                                        logging.debug('parent '+span_dict[parent][1][1]+' exe time '+str(span_dict[parent][0]))
                                else:
                                        logging.error('parent '+str(parent)+' or child '+str(child)+' is missing')

              # Get only root nodes from forest
              for node in G.nodes():
                    if span_dict[node][1][0] != process_id:
                            span_dict.pop(node, None)
              return span_dict   

        # Main difference from above method:
        # Here we assume that all elements will be present in the traces, but in real world it is observed that some trace ids are invalid.

        def sockshop_parse_span_json(self, span_json, process_id):
              span_dict = dict()
              G = nx.DiGraph()
              for span in span_json:
                   if span['operationName'] != 'error':
                       span_dict[span['spanID']] = [0,list()]
                       span_dict[span['spanID']][0] = int(span['duration'])
                       span_dict[span['spanID']][1].append(span['processID']) 
                       span_dict[span['spanID']][1].append(span['operationName'])
                       for reference in span['references']:
                             if reference['refType'] == 'CHILD_OF':
                                     G.add_edge(reference['spanID'],span['spanID'])
                   else:
                       logging.info("Their is error in operation ",span['operationName'])
              
              G1 = G.copy()
              for node in G.nodes():
                 if node not in span_dict.keys():
                      G1.remove_node(node)
              G = G1
              # Get count of parent nodes
              top_nodes = list()
              for node in G.nodes():
                    if node in span_dict.keys() and G.in_degree(node) == 0:
                         top_nodes.append(node)

              for node in top_nodes:              
                        parent = node
                        children = list(G.successors(parent))
                        for child in children:
                                if parent in span_dict.keys() and child in span_dict.keys():
                                        logging.debug('parent span_id '+parent+' '+span_dict[parent][1][1]+' exe time '+str(span_dict[parent][0]))
                                        logging.debug('child '+'span_id '+child+' '+span_dict[child][1][1]+' exe time '+str(span_dict[child][0]))
                                        span_dict[parent][0] = span_dict[parent][0] - span_dict[child][0]
                                        logging.debug('parent '+span_dict[parent][1][1]+' exe time '+str(span_dict[parent][0]))
                                else:
                                        logging.error('parent '+str(parent)+' or child '+str(child)+' is missing')

              # Get only root nodes from forest
              for node in G.nodes():
                    if G.in_degree(node) != 0:
                            span_dict.pop(node, None)
              return span_dict   

        def del_tree(self,graph,parent,span_dict):
                if len(list(graph.successors(parent))) == 0:
                         logging.debug("del_tree "+span_dict[parent][1][1])
                         if parent in graph.nodes():
                              graph.remove_node(parent)
                         else:
                              logging.error('parent '+str(parent)+' not in nodes')
                         return None
                else:
                    for child in list(graph.successors(parent)):
                            self.del_tree(graph,child,span_dict)
                            logging.debug("del_tree "+span_dict[parent][1][1])
                            if parent in graph.nodes():
                               graph.remove_node(parent)
                            else:
                               logging.error('parent '+str(parent)+' not in nodes')
        
        def parse_span_json_LogKV(self,span_json,process_id):
                span_dict = dict()

                G = nx.DiGraph()
                for span in span_json:
                        try:
                                if span['operationName'] != 'error':
                                        if len(span['logs']) != 0 and 'fields' in span['logs'][0].keys() and len(span['logs'][0]['fields']) != 0 and 'value' in span['logs'][0]['fields'][0].keys():
                                                                span_dict[span['spanID']] = [0,list()]
                                                                span_dict[span['spanID']][0] = float(span['logs'][0]['fields'][0]['value'])
                                                                span_dict[span['spanID']][1].append(span['processID']) 
                                                                span_dict[span['spanID']][1].append(span['operationName'])
                                        else:
                                          logging.debug("Their is error in operation "+str(span['operationName']))
                        except Exception as e:
                                logging.error(e)
                                logging.error(span)

                return span_dict
        
        # Intent:
        #  trace_json contains performance data for multiple related calls.
        #  we extract that data and create a lookup table with
        #  operator name as key and execution time 
        # Assumptions:
        # Structure of traces
        #   spans:
        #   processes:
        # service_name is name given in Jeager
        def parse_trace_json(self, trace_json, service_name):
               try:
                  process_ids =  self.parse_process_json(trace_json['processes'])
               except Exception as e:
                        logging.error(e)
               try:
                  if 'spans' in trace_json.keys() and service_name in process_ids.keys():
                        spans = self.parse_span_json_LogKV(trace_json['spans'],process_ids[service_name])
               except Exception as e:
                        logging.error(e)
                        spans = {}
               
               performance_dict = dict()
               for span in spans.values():
                      if span[1][0] == process_ids[service_name]:
                            if span[1][1] not in performance_dict.keys():
                                    performance_dict[span[1][1]] = list()
                            performance_dict[span[1][1]].append(span[0])
               return performance_dict

        # Intent:
        #   Each data file has multiple independent traces.
        #   Get data from parsing each trace json and merge results back.
        # Assumptions:
        #   query_json is just list of traces
        def parse_query_json(self, query_json, service_name):
                performance_dict = dict()
                for trace in query_json:
                        try:
                                trace_performance_dict = self.parse_trace_json(trace,service_name)
                        except Exception as e:
                                logging.error(e)
                        for operator, service_perf in trace_performance_dict.items():
                                if operator not in performance_dict.keys():
                                        performance_dict[operator] = list()
                                performance_dict[operator].extend(service_perf)
                return performance_dict

        # Intent:
        # call the Jeager API to get all traces between start_time and end_time.
        # if the request is success then pass the json for parsing
        # Assumptions:
        #  Structure of json
        #      data:
        def get_execution_times(self, service_name):
                logging.info("[Jeager] Started downloading run-time traces from Jeager for "+str(service_name))
                subprocess.call(['pkill kubectl'], shell=True)
                logging.info('[sleep] killed kubectl'+str(10))
                time.sleep(10)
                subprocess.call(['kubectl port-forward -n istio-system svc/jaeger-query 16686:16686&'], shell=True)
                logging.info('[sleep] port forward 16686 for jeager'+str(10))
                time.sleep(10)

                Jeager_query_url = self.Jeager_address+'?'+'service='+service_name+'&limit=10000'
                print Jeager_query_url
                try:
                   response = requests.get(Jeager_query_url)
                   print response
                except Exception as e:
                   logging.error('unable to contact Jeager server')
                   logging.error(e)
                   return
                
                # logging.info("[Jeager] Finished downloading run-time traces from Jeager for "+str(service_name))
                # f = open('../apps/hotel-reservation/result/data/1115/frontend.json', 'r')
                # response = json.load(f)
                # print len(self.parse_query_json(response['data'], service_name)['CheckAvailability'])
                # f.close()

                with open(service_name+'.json', 'w') as log_file:
                      json_obj = json.dumps(response.json(), indent=4)
                      print >> log_file, json_obj
       
                if response.status_code == 200:
                     try:
                        return self.parse_query_json(response.json()['data'], service_name)
                     except Exception as e:
                        logging.error(e)
                else:
                     logging.error("Jeager query not working "+Jeager_query_url)

        # Intent:
        # Read a json file from a experiment and get the performance value
        def get_execution_times_from_a_exp(self,exp_id, service_name): 
                f = open(ssot.get_app_path()+'/result/data/'+str(exp_id)+'/'+str(service_name)+'.json', 'r')
                response = json.load(f)
                f.close()
                try:
                     return self.parse_query_json(response['data'], service_name)
                except Exception as e:
                     logging.error(e)

#print Jeager_client().get_execution_times('url-shorten-service')
#print "result ",Jeager_client().get_execution_times_from_a_exp(4102,'home-timeline-service')
# print "result ",Jeager_client().get_execution_times_from_a_exp(334,'user')
# print "result ",Jeager_client().get_execution_times_from_a_exp(334,'catalogue')
