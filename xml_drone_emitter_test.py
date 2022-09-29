import requests

body = """<?xml version="1.0"?>
<UpdateInventoryRequest>
    <DataArea>
        <IWMInventoryProcess>
            <Warehouse>MAG3</Warehouse>
            <Location>M-05-02-03</Location>
            <Item>E546284</Item>
            <Quantity>1200000</Quantity>
            <LoginCode>aai</LoginCode>
        </IWMInventoryProcess>
    </DataArea>
</UpdateInventoryRequest>"""

headers = {'Content-Type': 'application/xml'}

url = 'http://127.0.0.1:8000/drone-endpoint' # changer l'URL ici au besoin
#url = 'https://iwmi.herokuapp.com/drone-endpoint'

r = requests.post(url, data=body.encode('utf-8'), headers=headers)
print(r)