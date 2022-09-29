import random
from bs4 import BeautifulSoup
import string
import requests

"""
Requirements :
beautifulsoup4==4.11.1
lxml==4.9.1
soupsieve==2.3.2.post1
"""

class DataElement:
    def __init__(self, **kwargs) -> None:
        self.xml = BeautifulSoup("", "xml")
        update = self.xml.new_tag("UpdateInventoryRequest")
        data = self.xml.new_tag("DataArea")
        inv = self.xml.new_tag("IWMInventoryProcess")
        warehouse = self.xml.new_tag("Warehouse")
        location = self.xml.new_tag("Location")
        item = self.xml.new_tag("Item")
        quantity = self.xml.new_tag("Quantity")
        logincode = self.xml.new_tag("LoginCode")

        warehouse.append(kwargs["warehouse"])
        location.append(kwargs["location"])
        item.append(kwargs["item"])
        quantity.append(kwargs["quantity"])
        logincode.append(kwargs["logincode"])

        inv.append(warehouse)
        inv.append(location)
        inv.append(item)
        inv.append(quantity)
        inv.append(logincode)
        data.append(inv)
        update.append(data)

        self.xml.append(update)

    def __str__(self) -> str:
        return self.xml.prettify()

# This generator doesn't require unicity of data, it can be a good start
# but location in warehouses, for example, may be identical.
letters = [char for char in string.ascii_letters if char.isupper()]
lower = [char for char in string.ascii_letters if char.islower()]
warehouse = ["MAG1", "MAG2", "MAG3"]
warehouses = lambda: random.choice(warehouse)
location = lambda: f"{random.choice(letters[0:11])}-{str(random.randint(0, 11)).zfill(2)}-{str(random.randint(0, 11)).zfill(2)}-{str(random.randint(0, 11)).zfill(2)}"
item = lambda: f"{random.choice(letters)}{str(random.randint(1, 1000000)).zfill(6)}"
quantity = lambda: str(random.randint(1, 300))
logincode = lambda: f"{random.choice(lower)}{random.choice(lower)}{random.choice(lower)}"

url = 'http://127.0.0.1:8000/drone-endpoint' # changer l'URL ici au besoin
headers = {'Content-Type': 'application/xml'}

for i in range(3):
    data = {
        "warehouse" : warehouses(),
        "location" : location(),
        "item" : item(),
        "quantity" : quantity(), 
        "logincode" : logincode()
    }
    d = DataElement(**data)
    r = requests.post(url, data=d.__str__(), headers=headers)
    #print(d.__str__())