import requests
import time
import logging
import base64
import subprocess
from random import choice

timeout = 10
def check(host,port):
    count = 30
    while count > 0:
        try:
            time.sleep(3)
            # reserve
            url = "http://"+host+":"+port+"/reservation?inDate=2015-04-06&outDate=2015-04-12&lat=38.0235&lon=-122.095&hotelId=4&customerName=1&username=Cornell_1&password=0123456789&number=1"
            payload = ''
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data = payload)
            print response.status_code,response
            if response.status_code != 200:
                continue
            print "done testing"
            return True
        except Exception as e:
            logging.error(e)
            count = count - 1
            time.sleep(6)
            logging.error("Service not ready")
            if count == 0:
              return False
            else:
              continue
        if count == 0:
            return False
    return True
#check('localhost','5000')
