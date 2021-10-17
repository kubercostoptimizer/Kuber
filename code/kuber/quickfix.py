import csv
from util import *
sys.path.append('../SSOT')
from conf import ssot

results_file_path = FOLDER_CHARACTER.join([ssot.get_app_path(), '/result','Data', 'results.csv'])

def load_performances():
        res = {}
        line_number = 0
        with open(results_file_path) as results_file:
            reader = csv.DictReader(results_file)
            for row in reader:
                try:
                    line_number = line_number + 1
                    
                    # read rows from the file
                    vm = row['vm_type']
                    service_combination_tup = parse_service_combination(row['service_combination'])
                    index = int(row['index'])
                    service = row['service_name']
                    api = row['API_name']
                    performance = float(row['performance_value(ms)'])

                    # fill in the dict with vm -> service_combination -> service -> api -> performance
                    if vm not in res:
                        res[vm] = {}
                    if service_combination_tup not in res[vm]:
                        res[vm][service_combination_tup] = {} # dictionary from service combination to service
                    if index not in res[vm][service_combination_tup]:
                        res[vm][service_combination_tup][index] = {} 
                    if service not in res[vm][service_combination_tup][index]: 
                        res[vm][service_combination_tup][index][service] = {}

                    res[vm][service_combination_tup][index][service][api] = performance

                except Exception as e:
                    logging.error('could not parse '+str(row)+' in line '+str(line_number))
                    logging.error(e)
                    pass
        
        return res


def fix_benchmark_data():
    result = load_performances()
    processed_data = {}

    for vm_name in result.keys():
        for sc in result[vm_name].keys():
            for index in result[vm_name][sc].keys():
                if vm_name not in processed_data.keys(): 
                   processed_data[vm_name] = {}
                if len(sc) not in processed_data[vm_name].keys():
                   processed_data[vm_name][len(sc)] = list()
                
                processed_data[vm_name][len(sc)].append(result[vm_name][sc][index].values())
    return processed_data

def store():
            csv_file_name = ssot.get_app_path()+"/result/Data/results_temp.csv"
            fieldnames = ['exp_id','index','service_combination', 'vm_type', 'service_name','API_name','performance_value(ms)']
            file = open(csv_file_name, mode='a+')
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            perf_data = fix_benchmark_data()

            for vm_name in ssot.get_vm_names():
                for sc in ssot.get_service_combinations():
               
                    index = 0
                    if vm_name in perf_data.keys() and len(sc) in perf_data[vm_name].keys():
                        for data_sc_vm in perf_data[vm_name][len(sc)]:
                            service_id = 0
                            for service in sc:
                                    if service_id < len(data_sc_vm):
                                        writer.writerow({'exp_id':int(10),'index':str(index),'service_combination': tuple([str(s) for s in sc]), 'vm_type': vm_name, 'service_name': service, 'API_name': 'run','performance_value(ms)': data_sc_vm[service_id]['run']})
                                        service_id = service_id + 1
                                    else:
                                        break
                            index = index + 1
                            if index >= 15:
                                break

store()