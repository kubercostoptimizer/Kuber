import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice
from time import sleep

class WebTasks(TaskSet):

    @task
    def load(self):
        base64string = base64.encodestring('%s:%s' % ('user', 'password')).replace('\n', '')

        self.client.get("/catalogue")
        item_id = "510a0d7e-8e83-4193-b483-e27e09ddc34d"
        self.client.get("/")
        self.client.get("/login", headers={"Authorization":"Basic %s" % base64string})
        self.client.get("/category.html")
        self.client.get("/detail.html?id={}".format(item_id))
        self.client.delete("/cart")
        self.client.post("/cart", json={"id": item_id, "quantity": 1})
        self.client.get("/basket.html")
        self.client.post("/orders")
        sleep(5)

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0
