import json
import requests

url = 'http://127.0.0.1:8000/adjustment'
# url = 'https://iwmi.herokuapp.com/adjustment'
headers = {'Content-Type': 'application/json'}

data = {
    "wid":"MAG1",
    "location":"K-02-03-01",
    "pid":"E546284",
    "quantity":67,
    "login":"aia",
}

d = json.dumps(data)
r = requests.post(url, json=data, headers=headers)