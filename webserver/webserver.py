from fastapi import APIRouter, Body, Request, Response, HTTPException, status, FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId

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


import uuid
from typing import Optional
from pydantic import BaseModel, Field
from typing import List

class Product(BaseModel):
    id: str = Field(str, alias="_id")
    label: str = Field(None,alias="label")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "123123132132132132",
                "label": "Don Quixote"
            }
        }


@IWMI_api.get("/product/{productID}", response_description="Get a single product by id", response_model=Product)
async def productsWithID(productID: str, request: Request):
    # todo : request all products and send it in the following form, using "productID" as id of the product :
    print(repr(ObjectId(productID)))
    if (product := request.app.database["product"].find_one({"_id": productID})) is not None:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {productID} not found")


