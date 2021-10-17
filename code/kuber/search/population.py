# population class
from solution import Solution
import sys
import copy


class Population():
    def __init__(self, id_t,services, cherrypick_data, p_size, d_rate, l_size, D_lower, D_upper, solutions=None):
        if solutions != None:
            self.solutions = solutions
        else:
            self.solutions = list()
        self.p_size = p_size
        self.d_rate = d_rate
        self.l_size = l_size
        self.D_lower = D_lower
        self.D_upper = D_upper
        self.services = services
        self.cherrypick_data = cherrypick_data
        self.id_t = id_t
      

    def generate_initial_population(self):
        while self.p_size != len(self.solutions):
            solution = Solution(self.services, self.cherrypick_data,self.d_rate, self.l_size, self.D_lower, self.D_upper)
            solution.solve()
            # solution.display()
            self.solutions.append(copy.deepcopy(solution))

    def best_solution(self):
        self.least_cost = self.solutions[0].cost()
        self.least_cost_solution = self.solutions[0]
        # self.least_cost_solution.display()
        for solution in self.solutions:
            # solution.display()
            if solution.cost() < self.least_cost:
                self.least_cost = solution.cost()
                self.least_cost_solution = solution
        return self.least_cost_solution.graph.solution,self.least_cost 

    def add_solution(self, solution):
        self.solutions.append(copy.deepcopy(solution))
        # solution.sortcost()

    def sortcost(self,solution):
        # solution.display()
        return solution.cost()

    def merge(self, new_population):
        self.solutions.extend(new_population.solutions)
        self.solutions.sort(key = self.sortcost)
        self.solutions = self.solutions[0:self.p_size]
