import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice
from time import sleep

class WebTasks(TaskSet):

    @task
    def load(self):
        self.client.get("/run")
        sleep(10) # think time

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0
