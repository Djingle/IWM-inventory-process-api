from fastapi import APIRouter, Body, Request, Response, HTTPException, status, FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

IWMI_api = FastAPI()

@IWMI_api.on_event("startup")
def startup_db_client():
    IWMI_api.mongodb_client = MongoClient(config["ATLAS_URI"])
    IWMI_api.database = IWMI_api.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@IWMI_api.get("/")
async def root():
    return { # example
        "message": "Welcome to the IWMInventoryProcess API! 😳️"
    }

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

@IWMI_api.get("/products/{productID}")
async def productsWithID(productID: str):
    # todo : request all products and send it in the following form, using "productID" as id of the product :
    print(productID)
    return { # example
        "id": "ABCD123",
        "warehouse": "XYZ",
        "location": "A-02-02-03",
        "stock": 200,
        "history": [
            {
                "action": "inventory",
                "timestamp": "2022-09-26 08:42:03.400",
                "value": 200,
                "login": "drone"
            },
            {
                "action": "adjustment",
                "timestamp": "2022-09-26 10:04:20.100",
                "value": "+5",
                "login": "sos"
            }
        ]
    }