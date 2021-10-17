import cPickle as pickle
import logging
import os

def evaluate(cpu, speed, ram):
    logging.info('[cost func] cost function is called')
    # BO run object is used as interface of cost function
    bo_run = None

    logging.info('[cost func] loading bo_run object')
    with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'rb') as f:
        bo_run = pickle.load(f)

    logging.info('[cost func] calling meets_perf') 
    
    # Run VM type in this iteration
    cost_func, constraints = bo_run.meets_perf(cpu, speed, ram)

    logging.info('[cost func] dumping bo_run object')
    with open('/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj', 'wb') as f:
            logging.info(os.stat("/wd/code/kuber/vm_type_selectors/BO_Matlab/shared_BO.obj").st_size)
            pickle.dump(bo_run, f)

    return cost_func, constraints
   
