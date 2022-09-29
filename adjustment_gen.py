import json
import requests

url = 'http://127.0.0.1:8000/adjustment'
headers = {'Content-Type': 'application/json'}

data = {
    "warehouseID":"MAG1",
    "locationID":"A-02-02-03",
    "itemID":"E961307",
    "itemQuantity":"98",
    "loginCode":"aia",
}

d = json.dumps(data)
r = requests.post(url, json=data, headers=headers)