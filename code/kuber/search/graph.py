import random
import itertools as itr
import copy

# TODO move this class somewhere else
class VM_type:
    def __init__(self, seed):
        random.seed(seed)
        self.type = seed
        self.cost = random.randint(1, 100)

class Node:
    def __init__(self, combination, vm_type):
        self.combination = combination
        self.vm_type = vm_type

# graph class
# this class provides an api to implement
# on demand the graph functions required to solve wid
class Graph:
    def __init__(self, services, cherrypick_data, partial_solution=None):
        self.services = services
        self.cherrypick_data = cherrypick_data # combination -> least cost VM type
        self.remaining_services = set(services)

        if partial_solution is None:
            self.solution = []
        else:
            self.solution = partial_solution
            for node in self.solution:
                self.remaining_services = self.remaining_services - node.combination
        
    def cost(self):
        res = 0
        for node in self.solution:
            res += node.vm_type['price']
        return res

    def has_remaining_services(self):
        if self.remaining_services:
            return True
        return False

    def least_cost_node(self):
        arg_max = 0
        res = None
        for combination in self.cherrypick_data:
            candidate = self.__maximal_subset(combination)
            vm_type = self.cherrypick_data[combination]
            if candidate:
                arg = self.__arg(candidate, vm_type)
                if arg > arg_max:
                    arg_max = arg
                    res = Node(candidate, vm_type)
        if arg_max == 0:
            raise Exception('Cannot add any other service combination')
        return res

    def __maximal_subset(self, combination):
        return set(combination).intersection(self.remaining_services)

    def __arg(self, combination, vm_type):
        neighbours = 2 ** len(self.remaining_services) - 2 ** (len(self.remaining_services) - len(combination)) 
        return neighbours / vm_type['price']

    def __set_to_bitmask(self, combination):
        res = 0
        for i in range(len(self.services)):
            if self.services[i] in combination:
                res += 1
            res *= 2
        return res

    def number_of_nodes(self):
        return 2 ** len(self.remaining_services) - 1

    # returns a list of k nodes
    def get_k_nodes(self, k):
        res = []
        res_set = set()
        for experiment_comb in self.cherrypick_data:
            maximal_subset = self.__maximal_subset(experiment_comb)
            vm_type = self.cherrypick_data[experiment_comb]
            for i in range(1, len(maximal_subset) + 1):
                for combination in itr.combinations(maximal_subset, i):
                    combination_set = set(combination)
                    encoded = self.__set_to_bitmask(combination_set)
                    if encoded not in res_set:
                        res_set.add(encoded)
                        res.append(Node(combination_set, vm_type))
                        if len(res) == k:
                            return res
        return res
        
    def add_to_solution(self, node):
        self.solution.append(node)
        self.remaining_services = self.remaining_services - node.combination

    def remove_from_solution_random(self):
        node_removed = self.solution.pop(random.randrange(len(self.solution)))
        self.remaining_services = self.remaining_services.union(node_removed.combination)