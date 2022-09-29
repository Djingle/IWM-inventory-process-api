import json
import requests

url = 'http://127.0.0.1:8000/adjustment'
headers = {'Content-Type': 'application/json'}

data = {
    "wid":"MAG1",
    "location":"A-02-02-03",
    "pid":"E961307",
    "quantity":"98",
    "login":"aia",
}

d = json.dumps(data)
r = requests.post(url, json=data, headers=headers)