from typing import List
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from bson import ObjectId
import re

######################## Database objects ########################
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



class Product(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    label: str = Field(None,alias="label")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "_id": "ObjectId(\"ab46513246546546578797\")",
                "label": "Don Quixote"
            }
        }


class ElementStorage(BaseModel):
    location: str = Field(None,alias="location")
    product_id : str = Field(None, alias="product_id")
    quantity : int = Field(None,alias="quantity")

class Storage(BaseModel):
    id: str = Field(None, alias="_id")
    warehouse: str = Field(None,alias="warehouse")
    stock: List[ElementStorage] = Field(None,alias="stock")
    

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "_id": "ObjectId(\"ab46513246546546578797\")",
                "warehouse": "MAG1",
                "location" : "A-02-02-03",
                "product_id" : "ObjectId(\"6332222fb6ed1eb4112e2061\")",
                "quantity" : "100"
            }
        }

class Warehouse(BaseModel):
    id: str = Field(None, alias="_id")
    totalStock:int = Field(None,alias="totalStock")
    totalItems:int = Field(None,alias="totalItem")

    class Config:
        schema_extra = {
            "example": {
                "_id": "MAG1",
                "totalStock": "125",
                "totalItems" : "3",
            }
        }

class Entry(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    pid: str = Field(None, alias="pid")
    date: datetime = Field(None, alias="date")
    wid: str = Field(None, alias="wid")
    movement_type: str = Field(None, alias="movement_type")
    quantity: int = Field(None, alias="quantity")
    location: str = Field(None,alias="location")
    login: str = Field(None,alias="login")

    # @validator('movement_type')
    # def movement_type_must_exists(cls, value):
    #     isValid = value == "in" or value == "out" or value == "adjust"
    #     if isValid:
    #         return value
    #     raise ValueError("movement_type is not of type 'in' or 'out' or 'adjust'")

    # @validator('wid')
    # def wid_is_valid(cls, value):
    #     if re.match('^MAG[0-9]$', value):
    #         return value
    #     raise ValueError("wid is not in a valid MAG<x> format.")

    @validator('pid')
    def pid_is_valid(cls, value):
        if re.match('^[A-Z][0-9]{6}$', value):
            return value
        raise ValueError("pid is not in a valid MAG<x> format.")


    class Config():
        json_encoders = { ObjectId: str }
        # allow_population_by_field_name = True
        # arbitrary_types_allowed = True
        schema_extra = {

        }
