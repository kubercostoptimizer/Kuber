import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice
from time import sleep

class WebTasks(TaskSet):

    @task
    def load(self):
          # search for a hotel  
          self.client.get("/hotels?inDate=2015-04-06&outDate=2015-04-12&lat=38.0235&lon=-122.095")

          # recommend a hotel
          self.client.get("/recommendations?require=rate&lat=38.0235&lon=-122.095")

          # user login
          self.client.get("/user?username=Cornell_1&password=0123456789")

          # reserve
          url = "/reservation?inDate=2015-04-06&outDate=2015-04-12&lat=38.0235&lon=-122.095&hotelId=4&customerName=1&username=Cornell_1&password=0123456789&number=1"
          payload = ''
          headers = {'Content-Type': 'application/x-www-form-urlencoded'}
          self.client.request("POST", url, headers=headers, data = payload)

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0

