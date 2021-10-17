from binary import binary
from Random import Random
from sort_find import sort_find
import bo_selector
from binary_optimized import binary_optimized
from prediction_selector import Prediction_selector
from Kuber_O import Kuber_O
from Kuber_O_1 import Kuber_O_1
from Kuber_O_1_C1 import Kuber_O_1_C1
from Kuber_O_1_C2 import Kuber_O_1_C2

class vm_type_selector:
    def __init__(self):
        self.bo_t = bo_selector.bo_t()

    def get(self,vm_type_selector):
        if vm_type_selector == 'binary':
            return binary
        elif vm_type_selector == 'binary_optimized':
            return binary_optimized
        elif vm_type_selector == 'random':
            return Random
        elif vm_type_selector == 'sort_find':
            return sort_find
        elif vm_type_selector == 'bo':
            return self.bo_t
        elif vm_type_selector == 'Prediction_selector':
            return Prediction_selector
        elif vm_type_selector == 'Kuber_O_1':
            return Kuber_O
        elif vm_type_selector == 'Kuber_O_1_1':
            return Kuber_O_1
        elif vm_type_selector == 'Kuber_O_1_C1':
            return Kuber_O_1_C1
        elif vm_type_selector == 'Kuber_O_1_C2':
            return Kuber_O_1_C2


vm_type_selector = vm_type_selector()