#!/usr/bin/env python
# coding: utf-8

# In[394]:

configs = [
    {
        "name": "cpu_count",
        "type": "INT",
        "size": 1,
        "min": 2,
        "max": 40
    },
    {
        "name": "ram",
        "type": "FLOAT",
        "size": 1,
        "min": 3.75,
        "max": 244
    },
    {
        "name": "speed",
        "type": "ENUM",
        "size": 1,
        "options": ["slow", "fast"]
    }
]
vms = [
    {
        "name": "r3.large",
        "cpu_count": 2,
        "ram": 15.25,
        "speed": "slow"
    },
    {
        "name": "r3.xlarge",
        "cpu_count": 4,
        "ram": 30.5,
        "speed": "slow"
    },
    {
        "name": "r3.2xlarge",
        "cpu_count": 8,
        "ram": 61,
        "speed": "slow"
    },
    {
        "name": "r3.4xlarge",
        "cpu_count": 16,
        "ram": 122,
        "speed": "slow"
    },
    {
        "name": "r3.8xlarge",
        "cpu_count": 36,
        "ram": 244,
        "speed": "slow"
    },
    {
        "name": "m4.large",
        "cpu_count": 2,
        "ram": 8,
        "speed": "slow"
    },
    {
        "name": "m4.xlarge",
        "cpu_count": 4,
        "ram": 16,
        "speed": "slow"
    },
    {
        "name": "m4.2xlarge",
        "cpu_count": 8,
        "ram": 32,
        "speed": "slow"
    },
    {
        "name": "m4.4xlarge",
        "cpu_count": 16,
        "ram": 64,
        "speed": "slow"
    },
    {
        "name": "m4.10xlarge",
        "cpu_count": 40,
        "ram": 160,
        "speed": "slow"
    },
    {
        "name": "i2.xlarge",
        "cpu_count": 4,
        "ram": 30.5,
        "speed": "slow"
    },
    {
        "name": "i2.2xlarge",
        "cpu_count": 8,
        "ram": 61,
        "speed": "slow"
    },
    {
        "name": "i2.4xlarge",
        "cpu_count": 16,
        "ram": 122,
        "speed": "slow"
    },
    {
        "name": "i2.8xlarge",
        "cpu_count": 36,
        "ram": 244,
        "speed": "slow"
    },
    {
        "name": "c4.large",
        "cpu_count": 2,
        "ram": 3.75,
        "speed": "fast"
    },
    {
        "name": "c4.xlarge",
        "cpu_count": 4,
        "ram": 7.5,
        "speed": "fast"
    },
    {
        "name": "c4.2xlarge",
        "cpu_count": 8,
        "ram": 15,
        "speed": "fast"
    },
    {
        "name": "c4.4xlarge",
        "cpu_count": 16,
        "ram": 30,
        "speed": "fast"
    },
    {
        "name": "c4.8xlarge",
        "cpu_count": 36,
        "ram": 60,
        "speed": "fast"
    }
]

# In[410]:


import numpy as np

def read_vms_normalize(configs, vms):
    lenvms = len(vms)
    lenconf = len(configs)
    vms_normalized = np.zeros((lenconf, lenvms))
    for configidx, config in enumerate(configs):
        name = config["name"]
        if config['type'] == 'INT' or config['type'] == "FLOAT":
            min = config['min']
            max = config['max']
            result = list(map(lambda vm: (vm[name] - min) / (max - min), vms))
            vms_normalized[configidx] = result
        if config["type"] == "ENUM":
            length = len(config['options'])
            index = []
            for vm in vms:
                enum = vm[name]
                for idx, option in enumerate(config['options']):
                    if option == enum:
                        index.append((idx) / (length - 1))
            vms_normalized[configidx] = index
    return np.array(vms_normalized).T


# In[414]:


def dist2(ls, x1, x2=None):
    # Assumes NxD and MxD matrices.
    # Compute the squared distance matrix, given length scales.
    if x2 is None:
        # Find distance with self for x1.
        # Rescale.
        xx1 = x1 / ls
        xx2 = xx1

    else:
        # Rescale.
        xx1 = x1 / ls
        xx2 = x2 / ls

    r2 = np.maximum(-(np.dot(xx1, 2 * xx2.T)
                      - np.sum(xx1 * xx1, axis=1)[:, np.newaxis]
                      - np.sum(xx2 * xx2, axis=1)[:, np.newaxis].T), 0.0)
    return r2


def Matern52(ls, x1, x2=None, grad=False):
    #     ls=np.array([1., 1., 1.])
    SQRT_5 = np.sqrt(5.0)
    r2 = np.abs(dist2(ls, x1, x2))
    r = np.sqrt(r2)
    cov = (1.0 + SQRT_5 * r + (5.0 / 3.0) * r2) * np.exp(-SQRT_5 * r)
    if grad:
        return None
    else:
        return cov


# In[415]:


vms_normalized = read_vms_normalize(configs, vms)

# print the result
for idx, vm1 in enumerate(vms_normalized):
    print("%10s" % vms[idx]['name'])
    for vm2 in vms_normalized:
        print("vm1", vm1)
        print("vm2", vm2)
        print([vm1, vm2])
        print(np.array([vm1, vm2]))
        print(
        "{:10.5f}".format(Matern52(ls=np.ones(len(configs)), x1=np.array([np.array(vm1), np.array(vm2)]))[0][1]), end
        = "")

# In[416]:

# input the data into the excle
import xlwt
from xlwt import Workbook

# Workbook is created
wb = xlwt.Workbook(encoding="utf-8")

# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('similarity')

for idx, vm in  enumerate(vms):
    sheet1.write(0, idx+1, str(vm['name']))
    sheet1.write(idx+1, 0, str(vm['name']))

for idx1, vm1 in enumerate(vms_normalized):
    for idx2, vm2 in enumerate(vms_normalized):
        result = Matern52(ls = np.ones(len(configs)),x1 = np.array([np.array(vm1),np.array(vm2)]))[0][1]
        sheet1.write(idx1 + 1, idx2 + 1, str(result))
wb.save('similarity.xls')


# In[417]:


# out put the histogram
point = []
vms_normalized = read_vms_normalize(configs, vms)
for idx, vm1 in enumerate(vms_normalized):
    for vm2 in vms_normalized:
        result = Matern52(ls=np.ones(len(configs)), x1=np.array([np.array(vm1), np.array(vm2)]))[0][1]
        result = round(result, 2)
        point.append(result)

import matplotlib.pyplot as plt

plt.hist(point, bins=50)
plt.gca().set(title='Frequency Histogram', ylabel='Frequency');

# In[328]:


from sklearn.cluster import KMeans
import numpy as np


kmeans = KMeans(n_clusters=4, random_state=0).fit(vms_normalized)


for idx, vm1 in enumerate(vms_normalized):
    print("%15s" %  vms[idx]['name'],"%10s" % vms[idx]['cpu_count'],
          "%15s" % vms[idx]['ram'],"%10s" % vms[idx]['speed'], end = " ")
    print("%15s" % kmeans.labels_[idx])


# In[303]:


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

plt.rcParams['figure.figsize'] = (16, 9)

# Creating a sample dataset with 4 clusters
X, y = make_blobs(n_samples=800, n_features=3, centers=4)
fig = plt.figure()

ax = Axes3D(fig)
ax.set_xlabel('cpu')
ax.set_ylabel('ram')
ax.set_zlabel('speed')

for idx, data in enumerate(vms_normalized):
    ax.scatter(vms_normalized[idx, 0], vms_normalized[idx, 1], vms_normalized[idx, 2],c='r',marker='o')
    ax.text(vms_normalized[idx, 0], vms_normalized[idx, 1], vms_normalized[idx, 2], vms[idx]['name'])
    pass


# In[ ]:




