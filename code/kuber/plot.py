import os
import sys
sys.path.append('../SSOT')
from conf import ssot
sys.path.append('../Experiment')
from experiment import experiment

class plot:
        def __init__(self):
            # Configuration
            self.app_name = ssot.get_app()
            self.figure_storage_folder = '/wd/code/apps/'+self.app_name+'/result/Kuber'
            self.number_images_folder = '/wd/code/Infrastructure/static/'
            
            # Book keeping
            self.global_service_str = ''
            self.global_groups = ''
            self.sc_index = 0
          
        def list_to_string(self,sc):
                service_str = ""
                for s in sc:
                    if s == '':
                        break
                    service_str = service_str+s+","
                return service_str

        def add_vm_types_column(self):
            vm_types_names = ssot.get_vm_names()
            vm_types_names.sort(key=ssot.get_vm_cost)
            service_str = "vm_types"
            previous_vm_type = ''

            group_string = "group { label = 'vm_types'; orientation= portrait; "
            for index, vm_name in enumerate(vm_types_names):
                  vm_name = ssot.print_vm_name(vm_name)
                  group_string = group_string+service_str+vm_name
                  group_string = group_string +' [label = "'+vm_name+'", width = 80, height = 80];\n'
                  group_string = group_string + service_str+previous_vm_type+" -> "+service_str+vm_name+' [dir = none]'+";\n"
                  previous_vm_type = vm_name
            
            # finish the service combination group
            group_string = group_string + "}"
            
            # connect service combinations in the figure
            self.global_groups = self.global_groups+' ' + group_string
            self.global_service_str = self.global_service_str+' '+service_str + ' -> '

        def add_sc_to_figure(self, sc, best_vm_type, current_experiments, propagated_experiments):
            
            # Get services as a string from a tuple (service1, service2,)
            service_str = self.list_to_string(sc)
 
            # Each service combination is added as a group into the figure
            group_string = "group { label = '"+str(self.sc_index)+"'; orientation= portrait; "
            self.sc_index = self.sc_index + 1

            # First symbol: service combination shown by a rectangle 
            group_string = group_string +service_str.replace(',', '')+' [label = "'+service_str+'", width = 160, height = 80];\n'

            previous_vm_type = ''
            
            # blockdiag can't take strings with commas as identifiers
            service_str = service_str.replace(',', '')
            
            # Composition of the figure
                # Executed for this service combination:
                    # Best VM type: green diamond
                    # Meets performance : green circle
                    # Not meets performance : red circle
                    # Note: Each VM type is numbered with order of execution
                # Propagated to this service combination from parent or child
                    # Propagated from parent
                        # Best VM type: pink diamond
                        # Other VM types: pink circle
                    # Propagated from child
                        # Best VM type: orange diamond
                        # Other VM types: orange circle
                # Other VM types
                    # Best VM type: white diamond
                    # Other VM types: white circle
            
            vm_types_names = ssot.get_vm_names()
            vm_types_names.sort(key=ssot.get_vm_cost)
            # for all available VM types
            for index, vm_name in enumerate(vm_types_names):
                group_string = group_string+service_str+vm_name.replace('.', '')
 
                # Experiments executed during this pass
                if vm_name in current_experiments.keys():
                    # print sc,vm_name,current_experiments[vm_name].meets_perf
                    if vm_name == best_vm_type:
                        group_string = group_string + ' [label = "",background ="'+self.number_images_folder+str(current_experiments[vm_name].index)+'.png", width = 80, height = 80, shape= "diamond", color = "green"];\n'
                    elif current_experiments[vm_name].meets_perf:
                        group_string = group_string + ' [label = "",background ="'+self.number_images_folder+str(current_experiments[vm_name].index)+'.png", width = 80, height = 80, shape= "circle", color = "green"];\n'
                    else:
                        group_string = group_string + ' [label = "",background ="'+self.number_images_folder+str(current_experiments[vm_name].index)+'.png", width = 80, height = 80,  shape= "circle", color = "red"];\n'
                
                # vm types imported from others
                elif vm_name in propagated_experiments.keys():
                    if propagated_experiments[vm_name]:
                        if vm_name == best_vm_type:
                            group_string = group_string +' [label = "" , width = 80, height = 80, shape= "diamond", color = "pink"];\n'
                        else:
                            group_string = group_string +' [label = "" , width = 80, height = 80, shape= "circle", color = "pink"];\n'
                    else:
                        if vm_name == best_vm_type:
                            group_string = group_string +' [label = "" , width = 80, height = 80, shape= "diamond", color = "orange"];\n'
                        else:
                            group_string = group_string +' [label = "" , width = 80, height = 80, shape= "circle", color = "orange"];\n'
                # vm types not executed  
                else:
                    if vm_name == best_vm_type:
                        group_string = group_string +' [label = "", width = 80, height = 80, shape= "diamond"];\n'
                    else:
                        group_string = group_string +' [label = "", width = 80, height = 80, shape= "circle"];\n'
                        
                # Connect VM types in the figure
                group_string = group_string + service_str+previous_vm_type+" -> "+service_str+vm_name.replace('.', '')+' [dir = none]'+";\n"
                previous_vm_type = vm_name.replace('.', '')
        
            # finish the service combination group
            group_string = group_string + "}"
            
            # connect service combinations in the figure
            self.global_groups = self.global_groups+' ' + group_string
            self.global_service_str = self.global_service_str+' '+service_str+ ' -> '

        def print_figure(self,exp_name):

            if not os.path.exists(self.figure_storage_folder):
                os.mkdir(self.figure_storage_folder)
            if not os.path.exists(self.figure_storage_folder+"/"+exp_name):
                os.mkdir(self.figure_storage_folder+"/"+exp_name)
            os.system("rm -f "+self.figure_storage_folder+"/"+exp_name+"/figure.txt")
            os.system("rm -f "+self.figure_storage_folder+"/"+exp_name+"/figure.png")
            
            diag_string = "blockdiag {"
            # attach all groups together and remove last -> symbol in each group
            diag_string = diag_string + self.global_groups + ' '+self.global_service_str[:-3]
            diag_string = diag_string + "} "
            
            try:
                with open(self.figure_storage_folder+"/"+exp_name+"/figure.txt", "w+") as f:
                    f.write(diag_string)
                # blockdiag is used to create diagrams from text
                os.system("blockdiag "+self.figure_storage_folder+"/"+exp_name+"/figure.txt")
            finally:
                f.close()
                diag_string = ''
                self.global_groups = ''
                self.global_service_str = ''
plot = plot()