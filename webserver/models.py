from pydantic import BaseModel, Field
from bson import ObjectId

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