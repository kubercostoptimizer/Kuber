import logging
import sys

class logconf:
        def print_console_log(self,level=logging.INFO):
                root = logging.getLogger()
                root.setLevel(level)
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(level)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                root.addHandler(handler)
        
logconf = logconf()
logconf.print_console_log()