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
            count = count - 1
            time.sleep(3)
            movie_index = 50
            user_index = 50
            username = "username_"+str(user_index)
            password = "password_"+str(user_index)
            #title = "Twilight"
            title = "P Storm"
            rating = 6
            text = "P storm review"
            #text = "There is nothing awesome about dolittle film. The only good part about this film is the special effects in making the animals look perfectly realistic. The story was very vague and there really wasn't any humor in this film. Mostly a film made for children only and not really an adult's cup of tea."
            url = "http://"+host+":"+str(port)+"/wrk2-api/review/compose"
            payload = "username="+username+"&password="+password+"&title="+title+"&rating="+str(rating)+"&text="+text
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.request("POST", url, headers=headers, data = payload)
            print url
            print response.status_code
            print response
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
#check('localhost','8080')