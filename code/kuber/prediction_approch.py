import numpy as np
from sklearn.ensemble import RandomForestRegressor

X = np.array([
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,2,1,0], 
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,2,2,0],
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,1,2,0], 
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,1,4,1],
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,2,4,0], 
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,2,8,1],
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,2,8,0], 
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,4,8,0],
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,4,16,1], 
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,8,16,0],
    [239.08,48.53,22.17,443869525.33,475077802.67,1081344.0,4.0,0.0,0.31,0.7,0.7,0.6029,306.7,15.0,7.72,32542282410.67,2367030272.0,2662400.0,7.25,0.04,0.18,0.52,0.52,0.3297,8,32,1],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,2,1,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,2,2,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,1,2,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,1,4,1],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,2,4,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,2,8,1],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,2,8,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,4,8,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,4,16,1],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,8,16,0],
    [241.3,48.63,22.85,438268416.0,470083925.33,1081344.0,4.42,0.0,0.33,0.66,0.65,0.2527,314.61,15.96,9.49,32524876117.33,2364408490.67,2662400.0,7.25,0.0,0.59,0.71,0.71,0.1447,8,32,1],
    [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,1,0],
    [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,1,0],
    [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,8,32,1],
    [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,8,32,1]
    ])

test_configs_user = np.array([
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,1,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,2,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,1,2,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,1,4,1],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,4,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,8,1],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,2,8,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,4,8,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,4,16,1],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,8,16,0],
                  [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.2657,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.1479,8,32,1]
                ])

test_configs_api = np.array([
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,1,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,2,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,1,2,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,1,4,1],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,4,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,8,1],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,2,8,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,4,8,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,4,16,1],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,8,16,0],
                      [233.2,54.33,25.77,397288789.33,431991978.67,501418.67,4.63,0.0,0.39,0.85,0.85,0.3975,313.08,15.36,8.05,32468560213.33,2365095082.67,2662400.0,7.0,0.0,0.24,0.5,0.5,0.2551,8,32,1]        
                    ])
cross_validation_user = np.array([0.2657, 0.1819, 0.1897, 0.5065, 0.2993, 0.1393, 0.144, 0.3295, 0.2062, 0.2182, 0.1479])
cross_validation_url = np.array([0.3975, 0.354, 0.2717, 0.3807, 0.6517, 0.3579, 0.5936, 0.6839, 0.4796, 0.218, 0.2551])
                                   
y = np.array([0.6029, 0.7476, 0.3696, 1.2888, 0.3468, 0.4226, 0.4469, 0.3045,0.4545,0.3202, 0.3297,0.2527,0.2811,0.1767,0.2237,0.1445,0.1268,0.1572,0.1138,0.1556,0.2927,0.1447,0.2657,0.3975,0.1479,0.2551])

model = RandomForestRegressor()
model.fit(X, y)

estimator = model.estimators_[5]

feature_names = ['VM1_CPU_idle','VM1_CPU_user','VM1_CPU_sys','VM1_Aval_mem','VM1_cache','VM1_buffer','VM1_Procs_running','VM1_Procs_blocked','VM1_load1','VM1_load5','VM1_load15','VM1_perf','VM11_CPU_idle','VM11_CPU_user','VM11_CPU_sys','VM11_Aval_mem','VM11_cache','VM11_buffer','VM11_Procs_running','VM11_Procs_blocked','VM11_load1','VM11_load5','VM11_load15','VM11_perf','VM_cores','VM_mem','Machine_type']


# from sklearn.tree import export_graphviz
# # Export as dot file
# export_graphviz(estimator, out_file='tree.dot', 
#                 feature_names = feature_names,
#                 rounded = True, proportion = False, 
#                 precision = 2, filled = True)

# # Convert to png using system command (requires Graphviz)
# from subprocess import call
# call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])

# # Display in jupyter notebook
# from IPython.display import Image
# Image(filename = 'tree.png')



mean_squ_error = 0

for i in range(0,11):
  yhat = model.predict([test_configs_user[i]])
  mean_squ_error = mean_squ_error + ((yhat - cross_validation_user[i])/cross_validation_user[i]) ** 2

print("Mean Squared Error: ",(mean_squ_error/11)*100, "%")


mean_squ_error = 0

for i in range(0,11):
  yhat = model.predict([test_configs_api[i]])
  mean_squ_error = mean_squ_error + ((yhat - cross_validation_url[i])/cross_validation_url[i]) ** 2

print("Mean Squared Error: ",(mean_squ_error/11)*100, "%")