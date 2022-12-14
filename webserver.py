from fastapi import APIRouter, Body, Request, Response, HTTPException, status, FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from typing import List
import xmltodict
from models import *
import json
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from fastapi.responses import HTMLResponse

######################## Server and Database connection initialisation ########################
config = dotenv_values(".env")

IWMI_api = FastAPI()

IWMI_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@IWMI_api.on_event("startup")
def startup_db_client():
    IWMI_api.mongodb_client = MongoClient(config["ATLAS_URI"])
    IWMI_api.database = IWMI_api.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@IWMI_api.on_event("shutdown")
def shutdown_db_client():
    IWMI_api.mongodb_client.close()

@IWMI_api.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>IWMInventoryProcess API</title>
            <style>body{margin:0;display:flex;justify-content:center;align-items:center;height:100vh;width:100vw;background-color:#222}*{font-family:sans-serif;text-align:center;color:#222}@keyframes changewidth{from{transform:rotate(180deg) scale(0);opacity:0}to{transform:rotate(360deg) scale(1);opacity:1}}body>div{animation-duration:1.0s;animation-name:changewidth;animation-iteration-count:start;background-color:#fff;margin:10px;padding:10px;border-radius:5px;max-width:calc(100vw - 40px)}img{width:min(100vw,100px)}a:hover{color:blue}</style>
        </head>
        <body>
        <div>
            <img src='https://cdn.discordapp.com/attachments/1016694266099146793/1024278535847809054/mamazon.png'>
            <h1>Welcome to the IWMInventoryProcess API!</h1>
            <a href='https://docs.google.com/document/d/1Sy-UleaDQPH3S5d4rBEHHHdNTQu0rXIwxFOnTpL8Q9s/edit?usp=sharing' target='blank_'>Documentation</a><br>
            <h2>Endpoint list</h2>
            <a href='./warehouse' target='blank_'>Warehouse</a><br>
            <a href='./warehouse/storage' target='blank_'>Warehouse storage</a><br>
            <a href='./product/' target='blank_'>Product</a><br>
            <a href='./entry/' target='blank_'>Entry</a><br>
            <a href='./drone-endpoint/' target='blank_'>Drone</a><br>
            <a href='./adjustment/' target='blank_'>Adjustment</a><br>
        </div>
        </body>
    </html>
    """


######################## Drone requests ########################
"""V??rifie si warehouseID existe"""
async def verify_warehouse(warehouseID:str,  req:Request):
    return req.app.database["storage"].find_one({"_id": warehouseID})

""""V??rifie que le productID existe"""
async def verify_product(productID:str,  req:Request):
    return req.app.database["product"].find_one({"_id": productID})

"""V??rifie : 1-Que le locationID existe dans le warehouseID et que le productID existe ?? cet endroit; 2 -Que le locationID existe dans le warehouseID et que la quantit?? est de 0 ?? cet endroit  """
async def verify_location(warehouseID:str,locationID:str,productID:str,req:Request):
    return list(req.app.database["storage"].aggregate([{"$unwind":"$stock"},{"$match":{"_id":warehouseID}},{"$match":{"$and" :[{"stock.location":locationID},{"$or" :[{"stock.quantity":0},{"stock.product_id":productID}]}]}}]))

"""V??rifie que le locationID existe dans le warehouse"""
async def verify_not_location(warehouseID:str,locationID:str,req:Request):
    return list(req.app.database["storage"].aggregate([{"$unwind":"$stock"},{"$match":{"_id":warehouseID}},{"$match":{"stock.location":locationID}}]))


@IWMI_api.post("/drone-endpoint")
async def droneEndpoint(req: Request, resp: Response):
    # expect an xml file
    if req.headers['Content-Type'] != 'application/xml':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported content type (XML only).")
    
    # retrieve request xml content
    xmlStr = await req.body()

    data = {}
    warehouseID = ""
    locationID = ""
    itemID = ""
    itemQuantity = ""
    loginCode = ""
    try:
        # parse xml string to a dict
        dictData = xmltodict.parse(xmlStr)
        data = dictData["UpdateInventoryRequest"]["DataArea"]["IWMInventoryProcess"]

        warehouseID = data["Warehouse"]
        locationID = data["Location"]
        itemID = data["Item"]
        itemQuantity = data["Quantity"]
        loginCode = data["LoginCode"]
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported XML format.")
    
    jsonDict = {
        "pid":itemID,
        "wid":warehouseID,
        "date":datetime.today(),
        "movement_type":"inventory",
        "quantity":itemQuantity,
        "location":locationID,
        "login":loginCode
    }
    
    #test = await verify_warehouse(warehouseID)
    test  =  await verify_warehouse(warehouseID, req)
    test2 =  await verify_product(itemID, req)
    test3 =  await verify_location(warehouseID, locationID, itemID, req)
    test4 =  await verify_not_location(warehouseID, locationID, req)

    if test is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please input an existing warehouse")

    if test2 is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please input an existing product")

    if len(test4) == 0:
        req.app.database["storage"].update_one({"_id":warehouseID},{"$push" : {"stock" :{"quantity": itemQuantity,"product_id" : itemID,"location" : locationID}}})
        req.app.database["entry"].insert_one(jsonDict)
        raise HTTPException(status_code=status.HTTP_200_OK)
    if len(test3)!=0:
        req.app.database["storage"].update_one({"_id":warehouseID,"stock.location" : locationID},{"$set" : {"stock.$.quantity" : itemQuantity}})

    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Another product existing at this location")

    req.app.database["entry"].insert_one(jsonDict)
    raise HTTPException(status_code=status.HTTP_200_OK)


######################## General requests ########################


@IWMI_api.get("/entry", response_description="Get a list of entries", response_model=List[Entry])
async def listEntries(request: Request):
    entries = list(request.app.database["entry"].find())
    return entries

######################## General requests ########################


@IWMI_api.post("/adjustment")
async def adjustment(req: Request, resp: Response):

    if req.headers['Content-Type'] != 'application/json':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported content type (json only).")

    reqB = {}
    wid = ""
    pid = ""
    location = ""
    quantity = ""
    try:
        reqB = await req.json()
        wid = reqB["wid"]
        pid = reqB["pid"]
        location = reqB["location"]
        quantity = reqB["quantity"]
        reqB["movement_type"] = "adjust"
        reqB["date"] = datetime.today()
    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported of invalid json format.")

    test =   await verify_warehouse(wid,req)
    print(test)
    test2 =  await verify_product(pid,req)
    print(test2)
    test3 =  await  verify_location(wid,location,pid,req)
    test4 =  await verify_not_location(wid,location,req)

    if test is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please input an existing warehouse")

    if test2 is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please input an existing product")
    if len(test4) == 0:
        req.app.database["storage"].update_one({"_id":wid},{"$push" : {"stock" :{"quantity": quantity,"product_id" : pid,"location" : location}}})
        req.app.database["entry"].insert_one(reqB)
        raise HTTPException(status_code=status.HTTP_200_OK)
    if len(test3)!=0:
        ll = list(req.app.database["storage"].aggregate([{"$unwind":"$stock"},{"$match":{"_id":wid}},{"$match":{"$and" :[{"stock.location":location},{"$or" :[{"stock.quantity":0},{"stock.product_id":pid}]}]}},{"$project":{"quantity":"$stock.quantity"}}]))
        value = ll[0]["quantity"]
        print(value)
        reqB["quantity"] = int(reqB["quantity"]) + value
        reqB["quantity"] = int(reqB["quantity"])
        req.app.database["storage"].update_one({"_id":wid,"stock.location" : location},{"$set" : {"stock.$.quantity" : reqB["quantity"]}})
        print("coucou", reqB)
        reqB["quantity"] = int(reqB["quantity"]) - value
    req.app.database["entry"].insert_one(reqB)

    raise HTTPException(status_code=status.HTTP_200_OK)


@IWMI_api.get("/product/{productID}", response_description="Get a single product by id", response_model=Product)
async def productsWithID(productID: str, request: Request):
    # todo : request all products and send it in the following form, using "productID" as id of the product :
    if (product := request.app.database["product"].find_one({"_id": productID})) is not None:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {productID} not found")

@IWMI_api.get("/product", response_description="List all Products", response_model=List[Product])
def list_products(request: Request):
    products = list(request.app.database["product"].find(limit=100))
    return products

@IWMI_api.get("/warehouse/storage", response_description="List all Storages", response_model=List[Storage])
def list_storages(request: Request):
    storages = list(request.app.database["storage"].find(limit=100))
    return storages

@IWMI_api.get("/warehouse/{warehouseID}/storage", response_description="List all Storages", response_model=Storage)
async def warehouseStorageWithID(warehouseID: str, request: Request):
    if (storage := request.app.database["storage"].find_one({"_id": warehouseID})) is not None:
        return storage
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Warehouse with ID {warehouseID} not found")


@IWMI_api.get("/warehouse", response_description="List total storage and items for each  warehouse ", response_model=List[Warehouse])
def list_warehouse(request: Request):
    aggregation = [{ "$unwind": "$stock" }, { "$group": { "_id": "$_id", "items": { "$addToSet": "$stock.product_id" },"totalStock":{"$sum":"$stock.quantity" } }},{"$project": {"_id":"$_id","totalStock":"$totalStock","totalItem":{"$size":"$items"}}}]
    warehouse = list(request.app.database["storage"].aggregate(aggregation))
    return warehouse

@IWMI_api.get("/warehouse/{warehouseID}", response_description="List total storage and items for a warehouse ", response_model=List[Warehouse])
def warehouseWithID(warehouseID:str,request: Request):
    aggregation = [{"$match":{"_id":warehouseID}},{ "$unwind": "$stock" }, { "$group": { "_id": "$_id", "items": { "$addToSet": "$stock.product_id" },"totalStock":{"$sum":"$stock.quantity" } }},{"$project": {"_id":"$_id","totalStock":"$totalStock","totalItem":{"$size":"$items"}}}]
    warehouse = list(request.app.database["storage"].aggregate(aggregation))
    return warehouse
