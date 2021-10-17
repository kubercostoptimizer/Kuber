# It should call the VM types and service combinations in same order
import sys
from cost_function import evaluate
sys.path.append('../SSOT')
from conf import ssot

class fake_bo:
    def __init__(self,service_combination):
        data = dict()
        data[(u'reservation',)] = ['t3.large','M6.large','a1.large','M6.medium','t3.micro','t3.small']
        data[(u'frontend',)] = ['t3.large','M6.xlarge','a1.2xlarge','a1.xlarge','t3.small','M6.large','M6.medium']
        data[(u'rate',)] =  ['t3.large','a1.large','M6.xlarge','M6.large','M6.medium','a1.medium']
        data[(u'reservation',u'frontend')] = ['M6.2xlarge','a1.xlarge','a1.2xlarge','a1.medium']
        data[(u'reservation',u'frontend',u'rate')] = ['a1.xlarge','M6.2xlarge','a1.2xlarge']
        vm_types_to_exe = data[service_combination]
        for vm_type in vm_types_to_exe:
            attrs = ssot.get_vm_type_attr(vm_type)
            evaluate(attrs['cpu'],attrs['computer'],attrs['ram'])
