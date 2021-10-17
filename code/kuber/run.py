# import matplotlib as mpl
# mpl.use('Agg')
import sys
import math
import copy
import subprocess
from kuber import Kuber
import csv
sys.path.append('../SSOT')
from conf import ssot
from util import * 
from experiment import experiment
from multiprocessing import Pool
import time
import csv
from Optimistic_solution import *

vm_type_selectors =['Kuber_O_1_C1']
propagations = ['noprop']#,'bottom']
global_budget = 150

#------------------------------------
# Functions over tracefiles
#------------------------------------
def write_to_result_file(filename,vm_type_selector,propagation,experiment_name,deployment_l,search_cost,num_experiments,num_WID_calls=0,budget_graph=False):
        deployment = deployment_l[0]
        deployment_cost = deployment_l[1]
        num_experiments = round(num_experiments,-1)
        if budget_graph:
                row_list = [deployment_cost*24*30,search_cost,num_experiments] 
        else:
                row_list = [get_row_name(vm_type_selector,propagation),deployment_cost*24*30,search_cost,num_experiments,num_WID_calls]

        for node in deployment: 
              row_list.append(str(node.combination))
              row_list.append(get_VM_nick_name(node.vm_type['name'])+'_'+experiment_name)
        
        file = open(filename, mode='a+')
        writer = csv.writer(file)
        writer.writerows([row_list])
        file.close()

def get_data_for_graphs(ars):
        vm_type_selector = ars[0]
        experiment_name = ars[1]
        propagation = ars[2]
        num_retries = 3
        file_name = '/results_budgets_'+str(vm_type_selector)+'_'+str(propagation)+'_'+str(experiment_name)+'.csv'
        results_path = FOLDER_CHARACTER.join([BASE_FOLDER, 'apps',ssot.get_app(), 'result','Kuber'])

        print file_name
        for i in range(0,50,1):
           for attempt_no in range(num_retries):
              try:
                print "Budget: ",i      
                deployment,search_cost,num_experiments = run_search(vm_type_selector,propagation,i,True,experiment_name)
                write_to_result_file(results_path+file_name,vm_type_selector,propagation,experiment_name,deployment,i,num_experiments,0,True)
                break
              except Exception as e:
                 print "skipping ..."+str(e)
                 deployment = [[],'']
                 num_experiments = 0
                 if attempt_no == num_retries-1:
                    write_to_result_file(results_path+file_name,vm_type_selector,propagation,experiment_name,deployment,1*i,num_experiments,0,True)

def plot_budget_graph(vm_type_selectors, propagations):
        data_inputs = []
        ssot.set_target_offset(0.5)
        for propagation in propagations:
                for vm_type_selector in vm_type_selectors:
                        get_data_for_graphs([vm_type_selector,'50p',propagation])


        
def run_search(vm_type_selector,propagation,budget,simulation,figure_name):
        print "Running ",vm_type_selector," ",propagation
        search = Kuber(vm_type_selector,propagation,budget,simulation)
        print "running search.run"
        deploymnet,search_cost,num_experiments = search.run()
        # search.store_trace_fig(figure_name)
        return deploymnet,search_cost,num_experiments 

#------------------------------------------------------------------------------------
# Functions to run exeperiments
#------------------------------------------------------------------------------------
def run_search_with_graph(vm_type_selector,propagation,budget,simulation,figure_name):
        print "Running ",vm_type_selector," ",propagation
        search = Kuber(vm_type_selector,propagation,budget,simulation)
        deploymnet,search_cost,num_experiments = search.run()
        # search.store_trace_fig(figure_name)
        return deploymnet,search_cost,num_experiments 

#------------------------------------------------------------------------------------
# Main function 
#------------------------------------------------------------------------------------
def main(simulation):

        results_path = FOLDER_CHARACTER.join([BASE_FOLDER, 'apps',ssot.get_app(), 'result','Kuber'])

        global vm_type_selectors
        global propagations 

  
        ssot.set_target_offset(0.5)
        for vm_type_selector in vm_type_selectors:
                for propagation in propagations:
                        # try:
                        deployment,search_cost,num_experiments = run_search_with_graph(vm_type_selector,propagation,global_budget,simulation,'50p')
                        # except Exception as e:
                        #         print e
                        #         continue
                        write_to_result_file(results_path+'/results.csv',vm_type_selector,propagation,'50p',deployment,search_cost,num_experiments)
                
        # if simulation:
        #     plot_budget_graph(ssot.get_app(),vm_type_selectors,propagations)
        

#import cProfile
main(True) 

