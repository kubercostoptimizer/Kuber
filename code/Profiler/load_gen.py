#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import os
import subprocess
import time
import sys
import logging
sys.path.append('../SSOT')
from conf import ssot 
from Jeager_client import Jeager_client as JC
from stats import stats

# todo change this path
dirPath  = os.path.dirname(os.path.abspath(__file__))

class load_gen:
    
    def __init__(self):
        self.host = ''
        self.port = ssot.get_port()
        self.limit_time = ssot.get_time_limit()
        self.concurrent = ssot.get_concurrent()
        self.perf_stat  = ssot.get_percentile()
        self.throughput  = ssot.get_throughput()
        pass

    def run(self,state,services):

        try:
            logging.info("[load gen] generating load on app "+''.join(services))
            start_load = self.start_load(self.host,self.port,self.concurrent,self.limit_time,self.throughput)
            basePath = "cd ../apps/"+ssot.get_app()+"/load_test"
            subprocess.call([basePath + " && " + start_load], shell=True)
            logging.info("[load gen] finished generating load on app "+''.join(services))

            highest_resp_time = 0
            state.init_exp_data()
            for service in services:
                JC().get_execution_times(service)
                state.save_data_files(service)
                
            return highest_resp_time
        except Exception as e:
            logging.error(e)

    def start_load(self,host,port,concurrent,limit_time,throughput):
        return "bash run.sh "+host+" "+port+" "+str(concurrent)+" "+str(limit_time)+" "+str(throughput)

load_gen = load_gen()