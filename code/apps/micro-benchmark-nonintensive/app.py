import requests
import time
import logging
import base64
import subprocess
from random import choice

timeout = 10
def check(host,port):
    count = 10
    while count > 0:
        try:
            time.sleep(3)
            # reserve
            url = "http://"+host+":"+port+"/run"
            response = requests.request("GET", url)
            print response.status_code
            if response.status_code != 200:
                continue
            return True
        except Exception as e:
            logging.error(e)
            count = count - 1
            time.sleep(6)
            logging.error("Service not ready")
            if count == 0:
                raise ValueError("Can't contanct the application")
    return True
#check("127.0.0.1","8081")
