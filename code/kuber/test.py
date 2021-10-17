from experiment import experiment
from conf import ssot
import sys
sys.path.append('../../../Profiler') #for unittests
sys.path.append('../Profiler')
from profiler import Profiler
import results_controller
from prediction import prediction

sys.path.append('../../vm_type_selectors')
sys.path.append('vm_type_selectors')
import combination_selector
from vm_type_selector import vm_type_selector 


# def get_analysis_on_sc(sc):
#     # results_controller_s = results_controller.results_controller('sort_find','bottom',False, 2000,True)
#     # print "SF: "+ssot.get_VM_nick_name(vm_type_selector.get('sort_find').run(sc,results_controller_s))+" Num exp: "+str(results_controller_s.total_number_experiments)

#     # results_controller_r = results_controller.results_controller('random','bottom',False, 2000,True)
#     # print "R: "+ssot.get_VM_nick_name(vm_type_selector.get('random').run(sc,results_controller_r))+" Num exp: "+str(results_controller_r.total_number_experiments)

#     # results_controller_b = results_controller.results_controller('binary','bottom',False, 2000,True)
#     # print "BS: "+ssot.get_VM_nick_name(vm_type_selector.get('binary').run(sc,results_controller_b))+" Num exp: "+str(results_controller_b.total_number_experiments)

#     results_controller_p = results_controller.results_controller('Prediction_selector','bottom',False, 2000,True)
#     results_controller_p.init_prediction()
#     results_controller_p.total_number_experiments = 0

#     result = vm_type_selector.get('Prediction_selector').run(sc,results_controller_p)

#     # if result is not None:
#     #     print "PR: "+ssot.get_VM_nick_name(result)+" Num exp: "+str(results_controller_p.total_number_experiments)

#     # TP = 0
#     # TN = 0
#     # FP = 0
#     # FN = 0

#     # for vm in ssot.get_vm_names():
#     #     meets_tar_pr = results_controller_p.predict_meets_target(sc,vm,'a1.medium','M6.2xlarge')
#     #     meets_tar_act = results_controller_p.get_result(sc,ssot.get_vm(vm))
#     #     if meets_tar_pr == meets_tar_act:
#     #         if meets_tar_act:
#     #             TP = TP +1
#     #         else:
#     #             TN = TN +1
#     #     else:
#     #         if meets_tar_pr:
#     #             FP = FP + 1
#     #         else:
#     #             FN = FN + 1

#     #     print ssot.get_VM_nick_name(vm),meets_tar_pr,meets_tar_act
    
#     # print TP,TN,FP,FN


# print experiment.meets_performance(('post-storage-service', 'user-mention-service'),'a1.large')
results_controller_p = results_controller.results_controller('Prediction_selector','bottom',False, 2000,True)
# results_controller_p.init_prediction()
# # results_controller_p.total_number_experiments = 0
# result = vm_type_selector.get('Prediction_selector').run(('user-service', 'social-graph-service'),results_controller_p)
# print result
# from vm_trace_logger import vm_trace_logger

# tracer = vm_trace_logger
# tracer.init('Prediction_selector','bottom',2000,results_controller_p,ssot.get_services()) 
# tracer.get_results_cache(2000)
# results_controller_p = tracer.results_controller
# results_controller_p.propagation_enabled = True
# print results_controller_p.propagation_enabled = True

#print results_controller_p.get_result(('social-graph-service','home-timeline-service','user-mention-service'),ssot.get_vm('a1.large'))
#print results_controller_p.get_result(('user-service','unique-id-service'),ssot.get_vm('a1.large'))
print prediction(results_controller_p).get_predictions(((u'user-service', u'social-graph-service'),'M6.medium','t3.small')
print prediction(results_controller_p).get_predictions(((u'user-service', u'write-home-timeline-service'),'M6.medium','t3.small')
print prediction(results_controller_p).get_predictions(((u'social-graph-service', u'write-home-timeline-service'),'M6.medium','t3.small')
print prediction(results_controller_p).get_predictions(((u'user-service', u'social-graph-service', u'write-home-timeline-service'),'M6.medium','t3.small')

# 'social-graph-service','post-storage-service','user-timeline-service','write-home-timeline-service','text-service'
# print results_controller_p.get_result(('media-service','url-shorten-service'),ssot.get_vm('a1.2xlarge'))
# print results_controller_p.get_result(('media-service','url-shorten-service','compose-post-service'),ssot.get_vm('a1.2xlarge'))
#print results_controller_p.get_result(('user-service','post-storage-service','"user-timeline-service','unique-id-service'),ssot.get_vm('a1.large'))

# print results_controller_p.get_result(('compose-post-service', 'media-service', 'url-shorten-service'),ssot.get_vm('a1.2xlarge'))
#print results_controller_p.get_result(("user-service", "social-graph-service", "post-storage-service", "user-timeline-service", "write-home-timeline-service", "home-timeline-service", "media-service", "unique-id-service", "url-shorten-service", "user-mention-service"),ssot.get_vm('t3.small'))
#print results_controller_p.get_result(("user-service", "social-graph-service", "post-storage-service", "user-timeline-service","compose-post-service", "write-home-timeline-service", "home-timeline-service", "media-service", "text-service", "unique-id-service", "url-shorten-service", "user-mention-service"),ssot.get_vm('M6.2xlarge'))

# print results_controller_p.get_result(("compose-post-service",),ssot.get_vm('t3.large'))
# print results_controller_p.get_result(("user-service", "social-graph-service", "post-storage-service", "user-timeline-service", "write-home-timeline-service", "home-timeline-service", "media-service", "text-service", "unique-id-service", "url-shorten-service", "user-mention-service"),ssot.get_vm('M6.xlarge'))



# get_analysis_on_sc(('user-service', 'url-shorten-service'))

# for vm in result.keys():
#     for service in result[vm].keys():
#         for api in result[vm][service].keys():
#             print vm,service,api,result[vm][service][api]

            
# print prediction(results_controller).get_predictions(('user-service', 'unique-id-service'),'t3.micro','M6.2xlarge')
# print prediction(results_controller).get_predictions(('user-service', 'user-mention-service'),'t3.micro','M6.2xlarge')
# print prediction(results_controller).get_predictions(('user-service', 'home-timeline-service'),'t3.micro','M6.2xlarge')

# ssot.set_target_offset(0.5)
#Profiler.execute(0,'t3.small',('home-timeline-service',))
# Profiler.execute(1,'t3.micro',('url-shorten-service',))
# Profiler.execute(2,'t3.micro',('url-shorten-service',))
# Profiler.execute(3,'t3.micro',('url-shorten-service',))
# # Profiler.execute(4,'t3.micro',('url-shorten-service',))

# # Profiler.execute(0,'t3.micro',('user-service',))
# # Profiler.execute(1,'t3.micro',('user-service',))
# # Profiler.execute(2,'t3.micro',('user-service',))
# # Profiler.execute(3,'t3.micro',('user-service',))
# # Profiler.execute(4,'t3.micro',('user-service',))

# # Profiler.execute(0,'t3.micro',('social-graph-service',))
# # Profiler.execute(1,'t3.micro',('social-graph-service',))
# # Profiler.execute(2,'t3.micro',('social-graph-service',))
# # Profiler.execute(3,'t3.micro',('social-graph-service',))
# # Profiler.execute(4,'t3.micro',('social-graph-service',))

# Profiler.execute(0,'t3.micro',('user-service','url-shorten-service'))
# #Profiler.execute(0,'t3.micro',('user-service',))
# # Profiler.execute(0,'t3.micro',('social-graph-service',))
# # Profiler.execute(0,'t3.micro',('post-storage-service',))
# # Profiler.execute(0,'t3.micro',('user-timeline-service',))
# # Profiler.execute(0,'t3.micro',('home-timeline-service',))
# # Profiler.execute(0,'t3.micro',('media-service',))
# # Profiler.execute(0,'t3.micro',('text-service',))
# # Profiler.execute(0,'t3.micro',('unique-id-service',))
# # Profiler.execute(0,'t3.micro',('write-home-timeline-service',))
# # Profiler.execute(0,'t3.micro',('user-mention-service',))

# Profiler.execute(0,'t3.small',('user-service','url-shorten-service'))
# #Profiler.execute(0,'t3.small',('user-service',))
# # Profiler.execute(0,'t3.small',('social-graph-service',))
# # Profiler.execute(0,'t3.small',('post-storage-service',))
# # Profiler.execute(0,'t3.small',('user-timeline-service',))
# # Profiler.execute(0,'t3.small',('home-timeline-service',))
# # Profiler.execute(0,'t3.small',('media-service',))
# # Profiler.execute(0,'t3.small',('text-service',))
# # Profiler.execute(0,'t3.small',('unique-id-service',))
# # Profiler.execute(0,'t3.small',('write-home-timeline-service',))
# # Profiler.execute(0,'t3.small',('user-mention-service',))

# Profiler.execute(0,'t3.large',('user-service','url-shorten-service'))
# #Profiler.execute(0,'t3.large',('user-service',))
# # Profiler.execute(0,'t3.large',('social-graph-service',))
# # Profiler.execute(0,'t3.large',('post-storage-service',))
# # Profiler.execute(0,'t3.large',('user-timeline-service',))
# # Profiler.execute(0,'t3.large',('home-timeline-service',))
# # Profiler.execute(0,'t3.large',('media-service',))
# # Profiler.execute(0,'t3.large',('text-service',))
# # Profiler.execute(0,'t3.large',('unique-id-service',))
# # Profiler.execute(0,'t3.large',('write-home-timeline-service',))
# # Profiler.execute(0,'t3.large',('user-mention-service',))

# Profiler.execute(0,'a1.medium',('user-service','url-shorten-service'))
# #Profiler.execute(0,'a1.medium',('user-service',))
# # Profiler.execute(0,'a1.medium',('social-graph-service',))
# # Profiler.execute(0,'a1.medium',('post-storage-service',))
# # Profiler.execute(0,'a1.medium',('user-timeline-service',))
# # Profiler.execute(0,'a1.medium',('home-timeline-service',))
# # Profiler.execute(0,'a1.medium',('media-service',))
# # Profiler.execute(0,'a1.medium',('text-service',))
# # Profiler.execute(0,'a1.medium',('unique-id-service',))
# # Profiler.execute(0,'a1.medium',('write-home-timeline-service',))
# # Profiler.execute(0,'a1.medium',('user-mention-service',))

# # Profiler.execute(0,'a1.large',('url-shorten-service',))
# Profiler.execute(0,'a1.large',('user-service','url-shorten-service'))
# # Profiler.execute(0,'a1.large',('social-graph-service',))
# # Profiler.execute(0,'a1.large',('post-storage-service',))
# # Profiler.execute(0,'a1.large',('user-timeline-service',))
# # Profiler.execute(0,'a1.large',('home-timeline-service',))
# # Profiler.execute(0,'a1.large',('media-service',))
# # Profiler.execute(0,'a1.large',('text-service',))
# # Profiler.execute(0,'a1.large',('unique-id-service',))
# # Profiler.execute(0,'a1.large',('write-home-timeline-service',))
# # Profiler.execute(0,'a1.large',('user-mention-service',))

# # Profiler.execute(0,'a1.xlarge',('url-shorten-service',))
# Profiler.execute(0,'a1.xlarge',('user-service','url-shorten-service'))
# # Profiler.execute(0,'a1.xlarge',('social-graph-service',))
# # Profiler.execute(0,'a1.xlarge',('post-storage-service',))
# # Profiler.execute(0,'a1.xlarge',('user-timeline-service',))
# # Profiler.execute(0,'a1.xlarge',('home-timeline-service',))
# # Profiler.execute(0,'a1.xlarge',('media-service',))
# # Profiler.execute(0,'a1.xlarge',('text-service',))
# # Profiler.execute(0,'a1.xlarge',('unique-id-service',))
# # Profiler.execute(0,'a1.xlarge',('write-home-timeline-service',))
# # Profiler.execute(0,'a1.xlarge',('user-mention-service',))

# # Profiler.execute(0,'a1.2xlarge',('url-shorten-service',))
# Profiler.execute(0,'a1.2xlarge',('user-service','url-shorten-service'))
# # Profiler.execute(0,'a1.2xlarge',('social-graph-service',))
# # Profiler.execute(0,'a1.2xlarge',('post-storage-service',))
# # Profiler.execute(0,'a1.2xlarge',('user-timeline-service',))
# # Profiler.execute(0,'a1.2xlarge',('home-timeline-service',))
# # Profiler.execute(0,'a1.2xlarge',('media-service',))
# # Profiler.execute(0,'a1.2xlarge',('text-service',))
# # Profiler.execute(0,'a1.2xlarge',('unique-id-service',))
# # Profiler.execute(0,'a1.2xlarge',('write-home-timeline-service',))
# # Profiler.execute(0,'a1.2xlarge',('user-mention-service',))

# # Profiler.execute(0,'M6.medium',('url-shorten-service',))
# Profiler.execute(0,'M6.medium',('user-service','url-shorten-service'))
# # Profiler.execute(0,'M6.medium',('social-graph-service',))
# # Profiler.execute(0,'M6.medium',('post-storage-service',))
# # Profiler.execute(0,'M6.medium',('user-timeline-service',))
# # Profiler.execute(0,'M6.medium',('home-timeline-service',))
# # Profiler.execute(0,'M6.medium',('media-service',))
# # Profiler.execute(0,'M6.medium',('text-service',))
# # Profiler.execute(0,'M6.medium',('unique-id-service',))
# # Profiler.execute(0,'M6.medium',('write-home-timeline-service',))
# # Profiler.execute(0,'M6.medium',('user-mention-service',))

# # Profiler.execute(0,'M6.large',('url-shorten-service',))
# Profiler.execute(0,'M6.large',('user-service','url-shorten-service'))
# # Profiler.execute(0,'M6.large',('social-graph-service',))
# # Profiler.execute(0,'M6.large',('post-storage-service',))
# # Profiler.execute(0,'M6.large',('user-timeline-service',))
# # Profiler.execute(0,'M6.large',('home-timeline-service',))
# # Profiler.execute(0,'M6.large',('media-service',))
# # Profiler.execute(0,'M6.large',('text-service',))
# # Profiler.execute(0,'M6.large',('unique-id-service',))
# # Profiler.execute(0,'M6.large',('write-home-timeline-service',))
# # Profiler.execute(0,'M6.large',('user-mention-service',))

# # Profiler.execute(0,'M6.xlarge',('url-shorten-service',))
# Profiler.execute(0,'M6.xlarge',('user-service','url-shorten-service'))
# # Profiler.execute(0,'M6.xlarge',('social-graph-service',))
# # Profiler.execute(0,'M6.xlarge',('post-storage-service',))
# # Profiler.execute(0,'M6.xlarge',('user-timeline-service',))
# # Profiler.execute(0,'M6.xlarge',('home-timeline-service',))
# # Profiler.execute(0,'M6.xlarge',('media-service',))
# # Profiler.execute(0,'M6.xlarge',('text-service',))
# # Profiler.execute(0,'M6.xlarge',('unique-id-service',))
# # Profiler.execute(0,'M6.xlarge',('write-home-timeline-service',))
# # Profiler.execute(0,'M6.xlarge',('user-mention-service',))

# # Profiler.execute(0,'M6.2xlarge',('url-shorten-service',))
# Profiler.execute(0,'M6.2xlarge',('user-service','url-shorten-service'))
# # Profiler.execute(0,'M6.2xlarge',('social-graph-service',))
# # Profiler.execute(0,'M6.2xlarge',('post-storage-service',))
# # Profiler.execute(0,'M6.2xlarge',('user-timeline-service',))
# # Profiler.execute(0,'M6.2xlarge',('home-timeline-service',))
# # Profiler.execute(0,'M6.2xlarge',('media-service',))
# # Profiler.execute(0,'M6.2xlarge',('text-service',))
# # Profiler.execute(0,'M6.2xlarge',('unique-id-service',))
# # Profiler.execute(0,'M6.2xlarge',('write-home-timeline-service',))
# # Profiler.execute(0,'M6.2xlarge',('user-mention-service',))

# # Profiler.execute(2,'a1.large',('url-shorten-service',,))
# # Profiler.execute(3,'t3.micro',('url-shorten-service',,))
# # Profiler.execute(4,'t3.micro',('url-shorten-service',,))

# # Profiler.execute(0,'t3.micro',('post-storage-service',))
# # Profiler.execute(1,'t3.micro',('post-storage-service',))
# # Profiler.execute(2,'t3.micro',('post-storage-service',))
# # Profiler.execute(3,'t3.micro',('post-storage-service',))
# # Profiler.execute(4,'t3.micro',('post-storage-service',))

# # Profiler.execute(0,'t3.micro',('user-timeline-service',))
# # Profiler.execute(1,'t3.micro',('user-timeline-service',))
# # Profiler.execute(2,'t3.micro',('user-timeline-service',))
# # Profiler.execute(3,'t3.micro',('user-timeline-service',))
# # Profiler.execute(4,'t3.micro',('user-timeline-service',))

# # Profiler.execute(0,'t3.micro',('home-timeline-service',))
# # Profiler.execute(1,'t3.micro',('home-timeline-service',))
# # Profiler.execute(2,'t3.micro',('home-timeline-service',))
# # Profiler.execute(3,'t3.micro',('home-timeline-service',))
# # Profiler.execute(4,'t3.micro',('home-timeline-service',))

# # Profiler.execute(0,'t3.micro',('media-service',))
# # Profiler.execute(1,'t3.micro',('media-service',))
# # Profiler.execute(2,'t3.micro',('media-service',))
# # Profiler.execute(3,'t3.micro',('media-service',))
# # Profiler.execute(4,'t3.micro',('media-service',))

# # Profiler.execute(0,'t3.micro',('text-service',))
# # Profiler.execute(1,'t3.micro',('text-service',))
# # Profiler.execute(2,'t3.micro',('text-service',))
# # Profiler.execute(3,'t3.micro',('text-service',))
# # Profiler.execute(4,'t3.micro',('text-service',))

# # Profiler.execute(0,'t3.micro',('unique-id-service',))
# # Profiler.execute(1,'t3.micro',('unique-id-service',))
# # Profiler.execute(2,'t3.micro',('unique-id-service',))
# # Profiler.execute(3,'t3.micro',('unique-id-service',))
# # Profiler.execute(4,'t3.micro',('unique-id-service',))

# # Profiler.execute(0,'t3.micro',('url-shorten-service',))
# # Profiler.execute(1,'t3.micro',('url-shorten-service',))
# # Profiler.execute(2,'t3.micro',('url-shorten-service',))
# # Profiler.execute(3,'t3.micro',('url-shorten-service',))
# # Profiler.execute(4,'t3.micro',('url-shorten-service',))

# # Profiler.execute(0,'t3.micro',('user-mention-service',))
# # Profiler.execute(1,'t3.micro',('user-mention-service',))
# # Profiler.execute(2,'t3.micro',('user-mention-service',))
# # Profiler.execute(3,'t3.micro',('user-mention-service',))
# # Profiler.execute(4,'t3.micro',('user-mention-service',))

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.large')
# #print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.2xlarge')
# #print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.2xlarge') #<- This should be the soultion

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.2xlarge')
# #print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.2xlarge') #<- This should be the soultion

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.2xlarge')
# #print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.2xlarge') #<- This should be the soultion

# # ssot.set_target_offset(0.8)
# # from targets import performance_targets
# # print 1/performance_targets.get_performance_target('comservice1','run')

# # ssot.set_target_offset(0.4)

# # print "1: ",experiment.meets_performance(('comservice1',),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1',),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1',),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1',),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1',),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1',),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1',),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1',),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice5',),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1',),'M6.xlarge') #<- This should be the soultion
# # print "11: ",experiment.meets_performance(('comservice1',),'a1.2xlarge')
# # print "12: ",experiment.meets_performance(('comservice1',),'M6.2xlarge')

# # print "1: ",experiment.meets_performance(('comservice1','comservice3'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice3'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice3'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice3'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice3'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice3'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice3'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice3'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice3'),'a1.xlarge') #<- This should be the soultion
# # print "10: ",experiment.meets_performance(('comservice1','comservice3'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice3'),'a1.2xlarge') 
# # print "12: ",experiment.meets_performance(('comservice1','comservice3'),'M6.2xlarge')

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.xlarge')  #<- This should be the soultion
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'a1.2xlarge')
# # print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3'),'M6.2xlarge')

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'a1.2xlarge')
# # print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4'),'M6.2xlarge') #<- This should be the soultion

# # print "1: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.micro')
# # print "2: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.small')
# # print "3: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.medium')
# # print "4: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.medium')
# # print "5: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.medium')
# # print "6: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.large')
# # print "7: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.large')
# # print "8: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'t3.large')
# # print "9: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.xlarge')
# # print "10: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.xlarge') 
# # print "11: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'a1.2xlarge')
# # print "12: ",experiment.meets_performance(('comservice1','comservice2','comservice3','comservice4','comservice5'),'M6.2xlarge') #<- This should be the soultion

