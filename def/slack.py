import requests
import json

def post(name, text, slack_post_url):
    requests.post(
        slack_post_url,
        data=json.dumps(
            {"text": text,
             "username": name,
             "icon_emoji": ":python:"}))
