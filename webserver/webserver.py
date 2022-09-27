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



######################## Server and Database connection initialisation ########################
config = dotenv_values(".env")

IWMI_api = FastAPI()

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
        "message": "Welcome to the IWMInventoryProcess API! 😳️"
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

        # todo : fill DB with those data
        print("XML received contains: ", warehouseID, locationID, itemID, itemQuantity, loginCode)

        return HTTPException(status_code=status.HTTP_200_OK)
    except:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported XML format.")


######################## General requests ########################
@IWMI_api.get("/warehouses")
async def warehouses():
    # todo : request all warehouses and send it in the following form :
    return { # example
        "warehouses": [
            {
                "id": "XYZ",
                "productsCount": 200,
                "totalStock": 1450
            },
            {
                "id": "UVW",
                "productsCount": 40,
                "totalStock": 200
            }
        ]
    }

@IWMI_api.get("/warehouses/{warehouseID}")
async def warehousesWithID(warehouseID: str):
    # todo : request all warehouses and send it in the following form, using "warehouseID" as id of the product :
    print(warehouseID)
    return {
        "id": "XYZ",
        "productsCount": 200,
        "totalStock": 1450,
        "inventory": { "products" : ["ABCD123", "EFGH456"] }
    }

@IWMI_api.get("/products")
async def products():
    # todo : request all products and send it in the following form :
    return { # example
        "products": [
            {
                "id": "XYZ",
                "productsCount": 200,
                "totalStock": 1450
            },
            {
                "id": "UVW",
                "productsCount": 40,
                "totalStock": 200
            }
        ]
    }



@IWMI_api.get("/product/{productID}", response_description="Get a single product by id", response_model=Product)
async def productsWithID(productID: PyObjectId, request: Request):
    # todo : request all products and send it in the following form, using "productID" as id of the product :
    if (product := request.app.database["product"].find_one({"_id": productID})) is not None:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {productID} not found")

@IWMI_api.get("/product", response_description="List all Products", response_model=List[Product])
def list_products(request: Request):
    products = list(request.app.database["product"].find(limit=100))
    return products



