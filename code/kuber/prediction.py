import sys
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from experiment import experiment
from targets import performance_targets
sys.path.append('../../../SSOT') #for unittests
sys.path.append('../SSOT')
from conf import ssot
import copy
import logging

class prediction:

    def __init__(self,results_controller):
         # For testing
        self.dry_run = True

        self.results_controller = results_controller

        # Two reference VMs, we are going to test on    
        self.Reference_VM1 = 'a1.medium' # performance will be some fraction of VM1s performance
        self.Reference_VM11 = 't3.micro'

        # Learning model we use in this prediction
        #self.model = RandomForestRegressor()
        self.model = RandomForestRegressor(random_state=0)

        # Collect initial data by running single services
        logging.info('[Prediction] getting training data')
        self.features,self.outputs = self.get_initial_training_data()

        # Train intial model
        logging.info('[Prediction] training the model')
        self.model.fit(np.array(self.features), np.array(self.outputs))


    
    # Read PARIS paper
    def get_fingerprint(self,VM1_results,VM2_results,service,api):

            if service not in VM1_results.keys() or api not in VM1_results[service][service].keys():
                print "service not in results"
                return None
            
            if service not in VM2_results.keys() or api not in VM2_results[service][service].keys():
                print "service not in results"
                return None

            # get lowest performance among all trails for each API
            api_performance_VM1 = VM1_results[service][service][api][0]
            metrics_VM1 = VM1_results[service][service][api][1]

            api_performance_VM2 = VM2_results[service][service][api][0]
            metrics_VM2 = VM2_results[service][service][api][1]

            if metrics_VM1 is None or metrics_VM2 is None:
                print "metrics are none"
                return None

            metrics_VM1.append(api_performance_VM1) 
            metrics_VM2.append(api_performance_VM2)
            
            fingerprint = metrics_VM1 + metrics_VM2

            return fingerprint

    # Read PARIS paper
    def get_fingerprint_prediction(self,VM1_results,VM2_results,service,api):

            if service not in VM1_results.keys() or api not in VM1_results[service].keys():
                print "service not in results"
                return None
            
            if service not in VM2_results.keys() or api not in VM2_results[service].keys():
                print "service not in results"
                return None

            # get lowest performance among all trails for each API
            api_performance_VM1 = VM1_results[service][api][0]
            metrics_VM1 = copy.deepcopy(VM1_results[service][api][1])

            api_performance_VM2 = VM2_results[service][api][0]
            metrics_VM2 = copy.deepcopy(VM2_results[service][api][1])

            if metrics_VM1 is None or metrics_VM2 is None:
                print "metrics are none"
                return None

            metrics_VM1.append(api_performance_VM1) 
            metrics_VM2.append(api_performance_VM2)
            
            fingerprint = metrics_VM1 + metrics_VM2

            return fingerprint

    def get_initial_training_data(self,combination=None):
        
        feature_list = []
        outputs = []
        results = {}
        
        services = combination

        if services is None:
            services = ssot.get_services()

        # execute all services on all VM types
        for vm_name in ssot.get_vm_names():
            if vm_name not in results.keys():
                results[vm_name] = {}

            for service in services:
                   logging.info('[Prediction] getting data for service '+str(service)+' on vm '+str(vm_name))
                   self.results_controller.get_result((service,),ssot.get_vm(vm_name))
                   result = self.results_controller.get_exper_data(vm_name,(service,))
                   if len(result) != 0:
                        results[vm_name][service] = result 
        
        # Gather training data from experiments
        for service in services:
            # Get performance and create different fingerprints for different APIs
            for api in performance_targets.get_apis_in_a_service(service):

                    target = performance_targets.get_performance_target(service,api)
                    if target != 0:
                        fingerprint = self.get_fingerprint(results[self.Reference_VM1],results[self.Reference_VM11],service,api)
                        if fingerprint is None:
                            continue

                        for vm_name in ssot.get_vm_names():
                            feature_list.append(fingerprint + ssot.get_vm_features(vm_name))
                            performance = results[vm_name][service][service][api][0]
                            outputs.append(performance)
         
        return feature_list,outputs                   
                   
    def get_predictions(self,service_combination,Reference_VM1,Reference_VM11):
       
            results = {}
            logging.info('[Prediction] getting data for service '+str(service_combination)+' on vm '+str(Reference_VM1))
            # self.results_controller.get_result(service_combination,ssot.get_vm(Reference_VM1))
            results_VM1 = self.results_controller.get_exper_data(Reference_VM1,service_combination)
            
            logging.info('[Prediction] getting data for service '+str(service_combination)+' on vm '+str(Reference_VM11))
            # execute and log the experiment before extracting the data
            # we only have to do this for second reference VM as first reference VM is checked and is he cheapest VM
            self.results_controller.get_result(service_combination,ssot.get_vm(Reference_VM11))
            results_VM2 = self.results_controller.get_exper_data(Reference_VM11,service_combination)

            logging.info('[Prediction] creating a fingerprint for '+str(service_combination))
            # Gather training data from experiments
            for service in service_combination:
                # Get performance and create different fingerprints for different APIs
                for api in performance_targets.get_apis_in_a_service(service):
                        target = performance_targets.get_performance_target(service,api)
                        if target != 0:
                        
                            fingerprint = self.get_fingerprint_prediction(results_VM1,results_VM2,service,api)
                            if fingerprint is None:
                                continue
                            # add data from two APIs to the existing training data
                            self.features.append(fingerprint + ssot.get_vm_features(Reference_VM1))
                            self.outputs.append(results_VM1[service][api][0])

                            self.features.append(fingerprint + ssot.get_vm_features(Reference_VM11))
                            self.outputs.append(results_VM2[service][api][0])

            #Retrain the model with new data
            self.model.fit(np.array(self.features), np.array(self.outputs))
            
            logging.info('[Prediction] recording prediction results for '+str(service_combination))
            for service in service_combination: 
                    # Get performance and create different fingerprints for different APIs
                    for api in performance_targets.get_apis_in_a_service(service):
                            target = performance_targets.get_performance_target(service,api)
                                                  
                            # Now predict for each VM type
                            for vm_name in ssot.get_vm_names():

                                if vm_name not in results.keys():
                                    results[vm_name] = {}

                                if service not in results[vm_name].keys():
                                    results[vm_name][service] = {}
                            
                                if api not in results[vm_name][service].keys():
                                    results[vm_name][service][api] = {}
                                
                                if target == 0:  
                                    results[vm_name][service][api] = 0
                                    continue
                                

                                fingerprint = self.get_fingerprint_prediction(results_VM1,results_VM2,service,api)
                                if fingerprint is None:
                                    continue
                                vm_config = fingerprint + ssot.get_vm_features(vm_name)
                                predicted_value = self.model.predict(np.array([fingerprint + ssot.get_vm_features(vm_name)]))
                                logging.info('vm_name '+str(vm_name)+' service '+str(service)+' api '+str(api)+' predicted value '+str(predicted_value))
                                results[vm_name][service][api] = predicted_value #* self.reference_performance[service][api] # convert from relative performance to actual performance
                        
            return results
    
    def get_prediction_accuracy(self,service_combination,Reference_VM1,Reference_VM11):
          predictions = self.get_predictions(service_combination,Reference_VM1,Reference_VM11)
       
          for service in service_combination: 
                # Get performance and create different fingerprints for different APIs
                for api in performance_targets.get_apis_in_a_service(service):
                     target = self.results_controller.get_lowest_performance('M6.2xlarge',service_combination, service, api)[0] * 2
                     mean_squ_error = 0
                     num_data_points = 0
                     for vm_name in ssot.get_vm_names():
                         num_data_points = num_data_points + 1
                         actual_value = self.results_controller.get_lowest_performance(vm_name,service_combination, service, api)
                         print actual_value[0],predictions[service][api][vm_name][0],target
                         mean_squ_error = mean_squ_error + ((predictions[service][api][vm_name][0] - actual_value[0])/actual_value[0]) ** 2
                     
                     print service+" "+api+" Mean Squared Error: "+str((mean_squ_error/num_data_points)*100)+ "%"

