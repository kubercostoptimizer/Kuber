import requests
import time
import logging
import base64
from random import choice

timeout = 10
def check(host,port):
    count = 10
    while count > 0:
        try:
            time.sleep(3)
            headers = {"Connection" : "close"}
            base64string = base64.encodestring('%s:%s' % ('user', 'password')).replace('\n', '')
            r = requests.get("http://"+host+":"+str(port)+ "/catalogue", timeout=timeout, headers=headers)
            logging.info("http://" + host + "/catalogue")
            logging.info(r)
            print "catalogue"
            if r.status_code != 200:
                continue
            item_id = "510a0d7e-8e83-4193-b483-e27e09ddc34d"
            r = requests.get("http://"+host+":"+str(port)+ "/", timeout=timeout, headers=headers)
            logging.info("http://" + host + "/")
            logging.info(r)
            print "/"
            if r.status_code != 200:
                continue
            r = requests.get("http://"+host+":"+str(port)+ "/login", timeout=timeout, headers={"Authorization": "Basic %s" % base64string, "Connection": "close"})
            logging.info("http://" + host + "/login")
            logging.info(r)
          
            r = requests.get("http://"+host+":"+str(port)+ "/category.html", timeout=timeout, headers=headers)
            logging.info("http://" + host + "/category.html")
            logging.info(r)
            if r.status_code != 200:
                continue
            r = requests.get("http://"+host+":"+str(port)+ "/detail.html?id={}".format(item_id), timeout=timeout, headers=headers)
            logging.info("http://" + host + "/detail.html")
            logging.info(r)
            if r.status_code != 200:
                continue
            r = requests.delete("http://"+host+":"+str(port)+ "/cart")
            logging.info("http://" + host + "/cart")
            logging.info(r)
            r = requests.post("http://"+host+":"+str(port)+ "/cart", json={"id": item_id, "quantity": 1}, timeout=timeout, headers=headers)
            logging.info("http://" + host + "/cart")
            logging.info(r)
            if r.status_code != 200 and r.status_code != 201:
                continue
            r = requests.get("http://"+host+":"+str(port)+ "/basket.html", timeout=timeout, headers=headers)
            logging.info("http://" + host + "/basket.html")
            logging.info(r)
            if r.status_code != 200:
                continue
            r = requests.get("http://"+host+":"+str(port)+ "/orders", timeout=timeout, headers=headers)
            logging.info("http://" + host + "/orders")
            logging.info(r)
            if r.status_code != 200 and r.status_code != 406 and r.status_code != 500:
                continue
            return True
        except Exception as e:
            logging.error(e)
            count = count - 1
            time.sleep(6)
            logging.error("Service not ready")
            return False
        if count == 0:
            return False
    return True

check('127.0.0.1','8081')
