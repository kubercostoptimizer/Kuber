import unittest
import sys
sys.path.append('../../')
import combination_selector

class combination_selector_ut(unittest.TestCase):
    def test_top(self):
        self.test_object = combination_selector.combination_selector("top")
        self.test_object.service_combinations = [('s1',),('s2',),('s1','s2')]
        self.assertEqual(self.test_object.get_next_combination(),('s1','s2'))
        self.assertEqual(self.test_object.get_next_combination(),('s2',))
        self.assertEqual(self.test_object.get_next_combination(),('s1',))
        self.assertEqual(self.test_object.get_next_combination(),None)  
    
    def test_bottom(self):
        self.test_object = combination_selector.combination_selector("bottom")
        self.test_object.service_combinations = [('s1',),('s2',),('s1','s2')]
        self.assertEqual(self.test_object.get_next_combination(),('s1',))
        self.assertEqual(self.test_object.get_next_combination(),('s2',))
        self.assertEqual(self.test_object.get_next_combination(),('s1','s2'))
        self.assertEqual(self.test_object.get_next_combination(),None) 

    def test_mix(self):
        self.test_object = combination_selector.combination_selector("mix")
        self.test_object.service_combinations = [('s1',),('s2',),('s1','s2')]
        self.assertEqual(self.test_object.get_next_combination(),('s1','s2'))
        self.assertEqual(self.test_object.get_next_combination(),('s1',))
        self.assertEqual(self.test_object.get_next_combination(),('s2',))
        self.assertEqual(self.test_object.get_next_combination(),None) 
    
    def test_noprop(self):
        self.test_object = combination_selector.combination_selector("noprop")
        self.test_object.service_combinations = [('s1',),('s2',),('s1','s2')]
        self.assertEqual(self.test_object.get_next_combination(),('s1','s2'))
        self.assertEqual(self.test_object.get_next_combination(),('s2',))
        self.assertEqual(self.test_object.get_next_combination(),('s1',))
        self.assertEqual(self.test_object.get_next_combination(),None)  

if __name__ == '__main__':
    unittest.main()