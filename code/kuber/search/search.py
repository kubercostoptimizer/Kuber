from population import Population
from graph import Graph, VM_type
import random
import time
import copy
import sys
from collections import OrderedDict
sys.path.append('../../../SSOT') #for unittests
sys.path.append('../../SSOT')
sys.path.append('../SSOT')
from conf import ssot

# population based search class
class PopulationBasedSearch:
    def __init__(self, services, data, p_size=1, d_rate=0.5, l_size=10, D_lower=30, D_upper=30, time_limit=40):
        self.p_size = p_size
        self.D_lower = D_lower
        self.D_upper = D_upper
        self.d_rate = d_rate
        self.l_size = ssot.get_num_combinations() #randomly select from all the combinations
        self.services = services
        self.cherrypick_data = data
        newlist = self.cherrypick_data.items()
        sortedlist = sorted(newlist, key=lambda s: len(s[0]))
        sortedlist = OrderedDict(sortedlist)
        
        # for sc,vm in sortedlist.items():
        #     print sc,vm['name']
        
        # print sortedlist
        self.population = Population(0,self.services, sortedlist, self.p_size, self.d_rate, self.l_size, self.D_lower, self.D_upper)
        self.population.generate_initial_population()
        self.time_limit = time_limit
        
    def solve(self):
        time_spent = 0
        time_start = time.time()
        id_t = 1
        print "Finding best configuration ..."
        while time_spent <= self.time_limit:
            new_population = Population(id_t,self.services, self.cherrypick_data, self.p_size, self.d_rate, self.l_size, self.D_lower, self.D_upper)
            for solution in self.population.solutions:
                solution = copy.deepcopy(solution)
                new_population.add_solution(solution.generate_offspring())
                # print solution.display()
            self.population.merge(copy.deepcopy(new_population))
            id_t = id_t + 1
            time_spent = time.time()-time_start
            #print "Time Done ", int((time_spent/self.time_limit)*100), "%"
        return self.population.best_solution()

class GreedySearch:
    def __init__(self, services, data):
        self.services = services
        self.data = data
        self.graph = Graph(services, data, partial_solution=None)

    def solve(self):
        while self.graph.has_remaining_services():
            node = self.graph.least_cost_node()
            self.graph.add_to_solution(node)
        return self.graph.solution, self.graph.cost()

# cherrypick_data = dict()
# cherrypick_data[(u'reservation')] = ssot.get_vm('t3.small')
# cherrypick_data[(u'reservation', u'recommendation')] = ssot.get_vm('t3.small')
# cherrypick_data[(u'recommendation')] = ssot.get_vm('t3.micro')

# wid_solution, cost = PopulationBasedSearch(ssot.get_services(),cherrypick_data).solve()
# for node in wid_solution: 
#         print str(node.combination)+" deployed on "+node.vm_type['name']