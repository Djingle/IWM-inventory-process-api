from fastapi import APIRouter, Body, Request, Response, HTTPException, status, FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from typing import List


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


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




class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    label: str = Field(None,alias="label")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "ObjectId(\"ab46513246546546578797\")",
                "label": "Don Quixote"
            }
        }


class storage(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    warehouse: str = Field(None,alias="warehouse")
    location: str = Field(None,alias="location")
    product_id : PyObjectId = Field(default_factory=PyObjectId, alias="product_id")
    quantity : int = Field(None,alias="quantity")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "ObjectId(\"ab46513246546546578797\")",
                "label": "Don Quixote"
            }
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


@IWMI_api.get("/product", response_description="List all Products", response_model=List[Product])
def list_products(request: Request):
    products = list(request.app.database["product"].find(limit=100))
    return products

