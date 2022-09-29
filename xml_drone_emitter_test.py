import requests

body = """<?xml version="1.0"?>
<UpdateInventoryRequest>
    <DataArea>
        <IWMInventoryProcess>
            <Warehouse>MAG1</Warehouse>
            <Location>A-02-02-03</Location>
            <Item>E961307</Item>
            <Quantity>100</Quantity>
            <LoginCode>aai</LoginCode>
        </IWMInventoryProcess>
    </DataArea>
</UpdateInventoryRequest>"""

headers = {'Content-Type': 'application/xml'}

url = 'http://127.0.0.1:8000/drone-endpoint' # changer l'URL ici au besoin
# url = 'https://iwmi.herokuapp.com/drone-endpoint'

r = requests.get(url, data=body.encode('utf-8'), headers=headers)