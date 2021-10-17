import sys
from vm_trace_logger import vm_trace_logger
sys.path.append('../SSOT')
from conf import ssot

ssot.set_target_offset(0.5)
vm_trace_logger.init('Prediction_selector','bottom',1000,None)
results_cache = vm_trace_logger.get_raw_data()
prediction_cache = []

for result in results_cache:
    sc = result[0]
    vm = result[1]
    meets_perf = result[2]
    is_executed = result[3]
    for result_child in prediction_cache: # look in already traversed list for children
            sc_child = result_child[0]
            vm_child = result_child[1]
            meets_perf_child = result_child[2]
            is_executed_child = result_child[3]
            if sc_child != sc and vm_child == vm and not meets_perf_child and is_executed_child and set(sc_child).issubset(sc):
                meets_perf = False
                is_executed = False
                print sc,sc_child,vm,vm_child,meets_perf_child,is_executed_child

    prediction_cache.append((sc,vm,meets_perf,is_executed))



for result in results_cache:
    sc = result[0]
    vm = result[1]
    meets_perf = result[2]
    is_executed = result[3]
    for result_child in new_results_cache: # look in already traversed list for children
            sc_child = result_child[0]
            vm_child = result_child[1]
            meets_perf_child = result_child[2]
            is_executed_child = result_child[3]
            if sc_child != sc and vm_child == vm and not meets_perf_child and is_executed_child and set(sc_child).issubset(sc):
                meets_perf = False
                is_executed = False
                print sc,sc_child,vm,vm_child,meets_perf_child,is_executed_child

    new_results_cache.append((sc,vm,meets_perf,is_executed))

# already_seen = {}

# vm_trace_logger.init('Prediction_selector','bottom',1000,None)
# vm_trace_logger.set_write_mode()
# for result in new_results_cache:
#     sc = result[0]
#     vm = result[1]
#     meets_perf = result[2]
#     is_executed = result[3]
#     if sc in already_seen.keys():
#         if vm in already_seen[sc].keys():
#             continue

#     # if sc not in already_seen.keys():
#     #     already_seen[sc] = {}
#     # already_seen[sc][vm] = [is_executed,sc]

#     # if vm == 'a1.medium' or vm == 't3.micro':
#     #     is_executed = True
#     vm_trace_logger.add_trace(is_executed,sc,ssot.get_vm(vm),meets_perf)
