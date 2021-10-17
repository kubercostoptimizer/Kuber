from graph import Graph
import random
import math

# solution class
class Solution:
    def __init__(self, services, cherrypick_data, d_rate, l_size, D_lower, D_upper, partial_solution=None):
        self.d_rate = d_rate
        self.l_size = l_size
        self.D_lower = D_lower
        self.Destruction_rate = D_lower
        self.D_upper = D_upper
        self.graph = Graph(services, cherrypick_data)

    def generate_offspring(self):
        offspring = Solution(self.graph.services, self.graph.cherrypick_data, self.d_rate,self.l_size,self.D_lower,self.D_upper, self.graph.solution)
        offspring.destroy_partially()
        offspring.solve()
        self.adapt(offspring)
        return offspring

    def destroy_partially(self):
        num_to_remove = int(max(3, math.floor(self.Destruction_rate * len(self.graph.solution))))
        for i in range(num_to_remove):
            if len(self.graph.solution) == 0:
                break
            self.graph.remove_from_solution_random()

    def adapt(self, offspring):
        if offspring.cost() < self.cost():
            self.Destruction_rate = self.D_lower
        else:
            self.Destruction_rate += 0.05 

    def solve(self):
       while self.graph.has_remaining_services():
            l = random.uniform(0, 1)
            next_node = None
            if l <= self.d_rate:
                next_node = self.graph.least_cost_node()
            else:
                self.l_size = 31
                num_of_nodes_to_select = min(self.graph.number_of_nodes(), self.l_size)
                k_nodes = self.graph.get_k_nodes(num_of_nodes_to_select)
                next_node = k_nodes[random.randint(0, len(k_nodes)-1)]
            self.graph.add_to_solution(next_node)

    def display(self):
        print "======================= start"
        for solution in self.graph.solution:
            print solution.combination,solution.vm_type['name']
        print "cost ",self.cost()
        print "======================= end"

    def cost(self):
        return self.graph.cost()