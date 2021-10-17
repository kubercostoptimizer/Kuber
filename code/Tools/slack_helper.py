import os
from slackclient import SlackClient

token = 'xoxp-253307662087-689626771877-766714345376-5b8ce534b8451167846a9f040b7057d6'

sc = SlackClient(token)

def send_message(text):
    sc.api_call("chat.postMessage", channel="monitoring", text=text)

