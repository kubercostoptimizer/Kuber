import base64

from locust import HttpLocust, TaskSet, task
from random import randint, choice
from time import sleep

class WebTasks(TaskSet):

    @task
    def load(self):
        movie_index = 50
        user_index = 50
        username = "username_"+str(user_index)
        password = "password_"+str(user_index)
        title = "Twilight"
        rating = 6
        text = "There is nothing awesome about Twilight film. The only good part about this film is the special effects in making the animals look perfectly realistic. The story was very vague and there really wasn't any humor in this film. Mostly a film made for children only and not really an adult's cup of tea."
        url = "/wrk2-api/review/compose"
        payload = "username="+username+"&password="+password+"&title="+title+"&rating="+str(rating)+"&text="+text
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.client.request("POST", url, headers=headers, data=payload)
        sleep(5)

class Web(HttpLocust):
    task_set = WebTasks
    min_wait = 0
    max_wait = 0

