import unittest

class search_ut(unittest.TestCase):
    
    def setUp(self):
            self.services = ["s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","s12"]
            self.cherrypick_data = self.get_cherrypick_data()

    def get_cherrypick_data(self):
            random.seed(103)
            cherrypick_data = {}
            for i in range(1, random.randint(1, 80)):
                combination = random.randint(1, 2**len(self.services))
                vm = VM_type(i)
                cherrypick_data[combination] = vm
            return cherrypick_data

    def test_greedy(self):
            greedy = SimpleGreedy(self.services,self.cherrypick_data)
            solution = greedy.solve()
            
    def test_population_based_search(self):
            p_size = 10
            D_lower = 30
            D_upper = 30
            d_rate = 0.5
            l_size = 10
            population_based_search = PopulationBasedSearch(self.services,self.cherrypick_data,p_size,d_rate,l_size,D_lower,D_upper,50)
            population_best = population_based_search.search()
