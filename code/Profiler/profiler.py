#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import subprocess
import os
import json
import base64
import logging
import numpy as np
import paramiko
from random import randint, choice
from test_infra import infra
from load_gen import load_gen
from experiment_state import state 
from datetime import datetime
from results_cache import results_cache

class Profiler:
    def __init__(self):
        self.initialized = False

    def init(self):
        # we need to execute this only for first time
        if not self.initialized:

            logging.config.fileConfig('/wd/code/SSOT/logging.conf')    
            start = datetime.now()
        
            # --------------------- Inital setup ----------------
            # create kube master and slave if not present
            infra.ensure_test_setup()
            
            # get our first experiment
            self.experiment = state.get_next_experiment()
            end = datetime.now()
            logging.info('Initial setup took '+str(end - start))
            # -----------------------------------------------------
            self.initialized = True
    
    def execute_all(self):
        """Run all service combinations
        This function will run all experiments (service combination -> VM pairs)
        if failed it will restart at the same experiment
        """
        self.init()
        logging.info("===================START EXPERIMENT========================")
        while self.experiment != None:
        
            start = datetime.now()
            # -------------------------------------------------

            vm_name = self.experiment[0]
            services = self.experiment[1]

            logging.info("[experiment] testing VM type "+vm_name)
            
            # --------------- Move the service ---------------
            # create a VM type to test
            _ , vm, host_name = infra.make_test_vmtype(vm_name)

            vm_ip = vm[0]
            vm_id = vm[1]

            logging.info("[experiment] testing service combination [ "+''.join(services)+" ]")
            
            infra.deploy_to_test_vmtype(services)

            # port forward the app to run load tests on it
            infra.expose_app()
            
            # test the APIs of the app
            infra.check_app_works()
    
            # ----------------- Load generation --------------
            # get ip of host where service is running
            load_gen.host = infra.get_ip_loadtest()

            # run the load test and record the performance
            performance = load_gen.run(state,services)
            # ------------------------------------------------

            # remove services from the VM
            infra.undeploy_to_test_vmtype(services)
            end = datetime.now()
            logging.info('Experiment '+str(experiment)+' took '+str(end - start))
            experiment = state.get_next_experiment()

        #infra.delete_test_setup()
        logging.info("===================END EXPERIMENT========================")


    def execute(self,index,vm_type,service_combination):
        """Executes load test while services in combination are on vm_type
        it handles infrastructure and load testing aspects for the combination under test
        """
        # try:
        # logging.info('line 97')
        #logging.info("[experiment] testing VM type "+vm_type['name'])

        service_combination = list(service_combination)
        self.init() 
        start = datetime.now()
        # -------------------------------------------------

        vm_name = vm_type
        services = service_combination
        state.set_current_experiment(vm_type,service_combination)
        
        # --------------- Move the service ---------------
        _ , vm, host_name = infra.make_test_vmtype(vm_name)

        vm_ip = vm[0]
        vm_id = vm[1]

        logging.info("[experiment] testing service combination [ "+''.join(services)+" ]")
        
        infra.deploy_to_test_vmtype(services)

        infra.expose_app()
        try:
            infra.check_app_works()
        except ValueError:
            if not infra.is_current_node_up():
               results_cache.store_node_failure(vm_type,service_combination)
               logging.error('Moving service combination brought node down')
               infra.delete_current_VM() #delete the VM thats down
               return

        # ----------------- Load generation --------------
        load_gen.host = infra.get_ip_loadtest()
        performance = load_gen.run(state,services)
        # ------------------------------------------------

        infra.undeploy_to_test_vmtype(services)
        end = datetime.now()

        results_cache.store(index,vm_type,service_combination)
        results_cache.store_metrics(index,infra.kube.get_metrics_instance_name(host_name),vm_name,service_combination)
        #state.save_experiment(vm_type,service_combination)
        
        logging.info('Running '+str(service_combination)+' on '+vm_name+' took '+str(end - start))
        
        # except Exception as e:
        #     logging.error(e)

Profiler = Profiler()