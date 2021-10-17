import unittest
import sys
sys.path.append('/wd/code/kuber/vm_type_selectors/BO_Matlab')
from cost_function import evaluate

class cost_function_ut(unittest.TestCase):
    def test_evaluvate(self):
        print evaluate('4','gen','8')

if __name__ == "__main__":
    unittest.main()
    