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
        if count == 0:
            return False
        try:
            print host,port
            count = count - 1
            time.sleep(3)
            url = "http://"+host+":"+str(port)+"/wrk2-api/post/compose"
            payload = 'username=username_353&user_id=353&text=wPFhpOym3fGNlC3lvRFM9KRgpmfndsCgXnR47PlMV7FtLUvt0q58Lbd2BmhqAqgxmLgvkIstRNodxYjxUskgOTyv4cbTcSMXzriSSlHtuNjWxIC1LrtkIpGQYw61DXS7NLImwfTieCOvzxfwbkz5W8c79jBSwmIMoyhpzZjcYMKNp51IdpWGuVAyrnJtBg56xptF4c9msJfcSr3NfzExurmpEughcosHljzdDlSB9NoA3qmyx2QW6MAb7NFk8N7h @username_669 http://IeTU2FiXGU19njQzuqKeMxzBpjegUT6tImSmrZpKh0JGhu9ciHn7qKZp9VbTklPN http://LagC4bRpbpNDhV9vEbzEtrDr10Oili7wlaBsIjc6QpOH6Uen5v10mEejEAbCLxBq&media_ids=&post_type=0'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data = payload)
            print url
            print response.status_code
            if response.status_code != 200:
                continue

            time.sleep(3)
            url = "http://"+host+":"+str(port)+"/wrk2-api/home-timeline/read?user_id=915&start=10&stop=20"
            payload = {}
            headers= {}
            response = requests.request("GET", url, headers=headers, data = payload)
            logging.info(url)
            logging.info(response)
            print url
            print response.status_code
            if response.status_code != 200:
                continue

            time.sleep(3)
            url = "http://"+host+":"+str(port)+"/wrk2-api/user-timeline/read?user_id=915&start=10&stop=20"
            payload = {}
            headers= {}
            response = requests.request("GET", url, headers=headers, data = payload)
            logging.info(url)
            logging.info(response)
            print url
            print response.status_code
            if response.status_code != 200:
                continue
            print "done testing"
            return True
        except Exception as e:
            logging.error(e)
            count = count - 1
            time.sleep(6)
            logging.error("Service not ready")
            return False
 
    return True
