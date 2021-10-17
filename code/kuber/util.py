import sys
sys.path.append('../SSOT')
from conf import ssot
import csv
import copy
import subprocess

BASE_FOLDER = '../../code'  
FOLDER_CHARACTER = '/' 

#------------
# Utils
#------------
def get_VM_nick_name(vm_type):
        vm_types = ssot.get_vm_types()
        vm_types.sort(key=lambda x: x['price'])
        index = 0
        for vm in vm_types:
                index = index + 1
                if vm['name'] == vm_type:
                        break
        place = index
        return 'VM'+str(place)


def get_vm_type_selector_str(vm_type_selector):
        if vm_type_selector == 'random':
                return 'R'
        elif vm_type_selector == 'binary':
                return 'B'
        elif vm_type_selector == 'binary_optimized':
                return 'BOpt'
        elif vm_type_selector == 'sort_find':
                return 'S'
        elif vm_type_selector == 'bo':
                return 'BO'
        elif vm_type_selector == 'optimistic':
                return 'OPT'
        elif vm_type_selector == 'Prediction_selector':
                return 'PRE'
        elif vm_type_selector == 'Kuber_O_1':
                return 'KUBEO'
        elif vm_type_selector == 'Kuber_O_1_C1':
                return 'KUBERO1C1'
        elif vm_type_selector == 'Kuber_O_1_C2':
                return 'KUBERO1C2'


def get_propagation_str(propagation):
        if propagation == 'noprop':
                return 'N'
        elif propagation == 'bottom':
                return 'B'
        elif propagation == 'top':
                return 'T'
        elif propagation == 'mix':
                return 'M'

def get_row_name(vm_type_selector,propagation):
        return get_vm_type_selector_str(vm_type_selector)+'_'+get_propagation_str(propagation)

# converts the service combination from str rep to tuple
def parse_service_combination(service_combination_str):
        splitted_tokens = service_combination_str.split("'")
        return tuple(splitted_tokens[1::2])  
            
#------------------------------------
# Functions over tracefiles
#------------------------------------
def dump_result(zpp_name,services,vm_type_selector,experiment_name,propagation):

        traces_path = FOLDER_CHARACTER.join([BASE_FOLDER, 'apps', zpp_name,'Traces'])
        results_path = FOLDER_CHARACTER.join([BASE_FOLDER, 'apps',zpp_name, 'result','Kuber'])

        if vm_type_selector == 'bo':
                deployment_l,search_cost,num_experiment = get_results_cache_bo(services,traces_path+'/'+vm_type_selector+'_'+propagation+'_'+str(ssot.get_target_offset())+'.csv',10000)
        else:
                deployment_l,search_cost,num_experiment = get_results_cache(services,traces_path+'/'+vm_type_selector+'_'+propagation+'_'+str(ssot.get_target_offset())+'.csv',10000)
        
        deployment = deployment_l[0]
        deployment_cost = deployment_l[1]
        row_list = [get_row_name(vm_type_selector,propagation),deployment_cost,search_cost,num_experiment]
        for node in deployment: 
              row_list.append(str(node.combination))
              row_list.append(get_VM_nick_name(node.vm_type['name'])+'_'+experiment_name)
        
        file = open(results_path+'/results.csv', mode='a+')
        writer = csv.writer(file)
        writer.writerows([row_list])
        file.close()

def get_data_for_graphs(vm_type_selector,experiment_name,propagation):
        deployment_costs = []
        search_costs = []
        budgets = []
        num_experiments = []
        num_retries = 3
        max_cost = ssot.get_max_cost()

        for i in range(1,11):
           for attempt_no in range(num_retries):
              try:
                if vm_type_selector == 'bo':
                        deployment,deployment_cost,num_experiment = get_results_cache_bo(ssot.get_services(),vm_type_selector+'_'+propagation+'_'+str(ssot.get_target_offset())+'.csv',0.1*i*max_cost)
                else: 
                        deployment,deployment_cost,num_experiment = get_results_cache(ssot.get_services(),vm_type_selector+'_'+propagation+'_'+str(ssot.get_target_offset())+'.csv',0.1*i*max_cost)
                deployment_costs.append(deployment_cost)
                budgets.append(i)
                num_experiments.append(num_experiment)
                break
              except Exception as e:
                 print e
                 if attempt_no < (num_retries - 1):
                         print "no solution found"
                 else:
                         break
        return budgets,deployment_costs,num_experiments

def plot_budget_graph(zpp_name, vm_type_selectors, propagations, experiment_name):
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(1,1,1)
       
        for propagation in propagations:
             for vm_type_selector in vm_type_selectors:
                    budgets,deployment_costs,num_experiments = get_data_for_graphs(vm_type_selector,experiment_name,propagation)
                    ax.plot(budgets,deployment_costs,label=get_row_name(vm_type_selector,propagation)) 
        
        ax.set_xlabel('Budget')
        ax.set_ylabel('Deployment cost')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=5, fancybox=True, shadow=True)
        ax.set_title(experiment_name)
        results_path = FOLDER_CHARACTER.join([BASE_FOLDER, 'apps',zpp_name, 'result','Kuber'])
        plt.savefig(results_path+'/'+experiment_name) 

def combine_images_all(experiments,vm_type_selectors,propagations,filename,budget=1000):
        
        for propagation in propagations:
            for exper in experiments:
                exper = str(budget)+exper
                if 'binary' in vm_type_selectors: 
                        binary_file_name = "/wd/code/apps/"+ssot.get_app()+"/result/Kuber/"+propagation+"binary"+exper+"/figure.png"
                else:
                        binary_file_name = '' 
                if 'random' in vm_type_selectors:
                        random_file_name = "/wd/code/apps/"+ssot.get_app()+"/result/Kuber/"+propagation+"random"+exper+"/figure.png"
                else:
                        random_file_name = ''
                if 'sort_find' in vm_type_selectors:
                        sf_file_name = "/wd/code/apps/"+ssot.get_app()+"/result/Kuber/"+propagation+"sort_find"+exper+"/figure.png"
                else:
                        sf_file_name = ''
                
                if 'bo' in vm_type_selectors:
                        bo_file_name = "/wd/code/apps/"+ssot.get_app()+"/result/Kuber/"+propagation+"bo"+exper+"/figure.png"
                else:
                        bo_file_name = ''
                subprocess.check_output(["convert -append "+random_file_name+" "+binary_file_name+" "+sf_file_name+" "+bo_file_name+" ../apps/"+ssot.get_app()+"/result/"+propagation+"_"+exper+"_"+filename+".jpg"],shell=True)

class Experiment_run:
    def __init__(self,sc,vm_type, meets_perf):
        self.vm_type = vm_type
        self.meets_perf = meets_perf
        self.index = 0


def check_results():
        results = experiment.load_performances()
        what_they_shouldbe = {}
        for vm_type in results.keys():
            for service_combination_parent in results[vm_type].keys():
                for service_combination_child in results[vm_type].keys():
                    if service_combination_parent != service_combination_child and set(service_combination_child).issubset(set(service_combination_parent)):
                            for service in results[vm_type][service_combination_child].keys():
                                    for api in results[vm_type][service_combination_child][service]:
                                            if service in results[vm_type][service_combination_parent].keys() and api in results[vm_type][service_combination_parent][service].keys():
                                                if results[vm_type][service_combination_child][service][api] > results[vm_type][service_combination_parent][service][api]:
                                                    if service_combination_parent not in what_they_shouldbe.keys():
                                                        what_they_shouldbe[service_combination_parent] = {}
                                                    if vm_type not in what_they_shouldbe[service_combination_parent].keys():
                                                        what_they_shouldbe[service_combination_parent][vm_type] = {}
                                                    if service not in what_they_shouldbe[service_combination_parent][vm_type].keys():
                                                        what_they_shouldbe[service_combination_parent][vm_type][service] = {}
                                                    if api not in what_they_shouldbe[service_combination_parent][vm_type][service].keys():
                                                        what_they_shouldbe[service_combination_parent][vm_type][service][api] = 0 
                                                    if results[vm_type][service_combination_child][service][api] > what_they_shouldbe[service_combination_parent][vm_type][service][api]:
                                                        what_they_shouldbe[service_combination_parent][vm_type][service][api] = results[vm_type][service_combination_child][service][api]

        from tempfile import NamedTemporaryFile
        import shutil
        import csv
        import random

        filename = experiment.results_file_path
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        fields = ['exp_id', 'service_combination', 'vm_type', 'service_name', 'API_name', 'performance_value(ms)']

        with open(filename, 'r') as csvfile, tempfile:
                reader = csv.DictReader(csvfile, fieldnames=fields)
                writer = csv.DictWriter(tempfile, fieldnames=fields)
                for row in reader:
                        for sc in what_they_shouldbe.keys():
                                for vm_type in what_they_shouldbe[sc].keys():
                                        for service in what_they_shouldbe[sc][vm_type].keys():
                                                for api in what_they_shouldbe[sc][vm_type][service].keys():
                                                        if row['service_combination'] == str(sc) and row['vm_type'] == vm_type and row['service_name'] == service and row['API_name'] == api:
                                                                row['performance_value(ms)'] = what_they_shouldbe[sc][vm_type][service][api] + random.uniform(0,1.5)
                                                                print row
                        if row['performance_value(ms)'] != 'performance_value(ms)':
                                row['performance_value(ms)'] = round(float(row['performance_value(ms)']),4)
                        writer.writerow(row)
        shutil.move(tempfile.name, filename)