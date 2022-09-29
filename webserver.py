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
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

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

@IWMI_api.get("/")
async def root():
    return { # example
        "message": "Welcome to the IWMInventoryProcess API! 😳️",
        "illustration": "https://cdn.discordapp.com/attachments/1016694266099146793/1024278535847809054/mamazon.png"
        # "documentation": ""
    }


######################## Drone requests ########################






@IWMI_api.get("/drone-endpoint")
async def droneEndpoint(req: Request, resp: Response):
    # expect an xml file
    if req.headers['Content-Type'] != 'application/xml':
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported content type (XML only).")
    
    # retrieve request xml content
    xmlStr = await req.body()
    
    try:
        # parse xml string to a dict
        dictData = xmltodict.parse(xmlStr)
        data = dictData["UpdateInventoryRequest"]["DataArea"]["IWMInventoryProcess"]

        warehouseID = data["Warehouse"]
        locationID = data["Location"]
        itemID = data["Item"]
        itemQuantity = data["Quantity"]
        loginCode = data["LoginCode"]
        
        jsonDict = {
            "pid":itemID,
            "wid":warehouseID,
            "date":datetime.today(),
            "movement_type":"adjust",
            "quantity":itemQuantity,
            "location":locationID,
            "login":loginCode
        }
        
        #test = await verify_warehouse(warehouseID)
        test = req.app.database["storage"].find_one({"_id": warehouseID})
        print(test is None)
        response =HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if( test is None):
            response = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Please input an existing warehouse")
        else :
            req.app.database["entry"].insert_one(jsonDict)

        return response
    except:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported XML format.")



######################## General requests ########################


@IWMI_api.get("/entry", response_description="Get a list of entries", response_model=List[Entry])
async def listEntries(request: Request):
    entries = list(request.app.database["entry"].find())
    return entries

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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {warehouseID} not found")





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




