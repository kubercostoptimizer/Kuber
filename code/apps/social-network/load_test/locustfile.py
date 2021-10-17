import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice
from time import sleep

class WebTasks(TaskSet):

    @task
    def load(self):
        self.client.get("/wrk2-api/home-timeline/read?user_id=915&start=10&stop=20")
        url = "/wrk2-api/post/compose"
        payload = 'username=username_353&user_id=353&text=wPFhpOym3fGNlC3lvRFM9KRgpmfndsCgXnR47PlMV7FtLUvt0q58Lbd2BmhqAqgxmLgvkIstRNodxYjxUskgOTyv4cbTcSMXzriSSlHtuNjWxIC1LrtkIpGQYw61DXS7NLImwfTieCOvzxfwbkz5W8c79jBSwmIMoyhpzZjcYMKNp51IdpWGuVAyrnJtBg56xptF4c9msJfcSr3NfzExurmpEughcosHljzdDlSB9NoA3qmyx2QW6MAb7NFk8N7h @username_669 http://IeTU2FiXGU19njQzuqKeMxzBpjegUT6tImSmrZpKh0JGhu9ciHn7qKZp9VbTklPN http://LagC4bRpbpNDhV9vEbzEtrDr10Oili7wlaBsIjc6QpOH6Uen5v10mEejEAbCLxBq&media_ids=&post_type=0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.client.request("POST", url, headers=headers, data = payload)

        sleep(5)

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0
