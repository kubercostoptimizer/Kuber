#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

# In[2]:


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
        return (cov, grad_Matern52(ls, x1, x2))
    else:
        return cov


# In[9]:

import numpy as np
import time

def dist_eclud(vec_a, vec_b):
    return np.sqrt(np.sum(np.power(vec_a - vec_b, 2)))

def matern52(vec_a, vec_b):
    # return Matern52(ls = np.ones(len(configs)),x1 = np.array([np.array(vec_a),np.array(vec_b)]))[0][1]
    resule = Matern52(np.array([1., 1., 1.]), x1=np.array([vec_a, vec_b]))
    return resule[0][1]


# to init the center by random
def rand_cent(data_set, k):
    m = np.shape(data_set)[1]
    center = np.array(np.zeros((k, m)))
    for col in range(m):
        min_col = min(data_set[:, col])
        max_col = max(data_set[:, col])
        center[:, col] = min_col + float((max_col - min_col)) * np.random.rand(k)
    print(center)
    return center


def kmeans(data_set, k, dist_method=matern52, cent_methon=rand_cent):
    sample_count = np.shape(data_set)[0]
    is_change = True
    keep_result = np.mat(np.zeros((sample_count, 2)))
    center_roids = cent_methon(data_set, k)
    while is_change:
        is_change = False
        for sample_index in range(sample_count):
            min_dist, min_index = np.Inf, -1
            for j in range(k):
                dist_j = dist_method(data_set[sample_index, :], center_roids[j, :])
                if dist_j < min_dist:
                    min_dist, min_index = dist_j, j
            if keep_result[sample_index, 0] != min_index:
                is_change = True
            keep_result[sample_index, :] = min_index, min_dist
        for cent_index in range(k):
            temp_cluster = data_set[np.nonzero(keep_result[:, 0].A == cent_index)[0]]
            if temp_cluster is not None:
                center_roids[cent_index, :] = np.mean(temp_cluster, axis=0)
        print(center_roids)
        print(keep_result)
        print("-------------")
        time.sleep(1)
    return keep_result


# In[ ]:

data_set = read_vms_normalize(configs, vms)
result = kmeans(data_set, 4)
print(result)

# In[ ]:


# In[ ]:
