from typing import List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema_generator):
        return {"type": "string"}

class LineItem(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "Request Item": "Brass Nut 1/2\" 20mm Galvanized Coarse",
                "Quantity": 143,
                "Amount": 143,
                "Unit Price": None,
                "Total": None,
                "matched_item": "Brass Nut 1/2\" 20mm Galvanized Coarse",
                "match_score": 100,
                "alternate_matches": [
                    {"match": "Brass Nut 1/2\" 30mm Galvanized Coarse", "score": 95.5}
                ]
            }
        }
    )

    request_item: str = Field(..., alias="Request Item")
    quantity: Optional[int] = Field(None, alias="Quantity")
    amount: Optional[int] = Field(None, alias="Amount")
    unit_price: Optional[float] = Field(None, alias="Unit Price")
    total: Optional[float] = Field(None, alias="Total")
    matched_item: Optional[str] = None
    match_score: Optional[float] = None
    alternate_matches: List[Dict[str, Any]] = []

class SalesOrderModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "60d5ec9af682dbd12a1b3456",
                "order_number": "SO-12345",
                "customer_name": "ACME Inc.",
                "order_date": "2023-05-01T00:00:00",
                "file_name": "sample_order.pdf",
                "line_items": [],
                "created_at": "2023-05-01T12:00:00",
                "updated_at": "2023-05-01T12:00:00"
            }
        }
    )

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    order_number: Optional[str] = None
    customer_name: Optional[str] = None
    order_date: Optional[datetime] = None
    file_name: str
    line_items: List[LineItem]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "60d5ec9af682dbd12a1b3456",
                "order_number": "SO-12345",
                "customer_name": "ACME Inc.",
                "order_date": "2023-05-01T00:00:00",
                "file_name": "sample_order.pdf",
                "line_items": [],
                "created_at": "2023-05-01T12:00:00",
                "updated_at": "2023-05-01T12:00:00"
            }
        }
    )

    id: str = Field(..., alias="_id")
    order_number: Optional[str] = None
    customer_name: Optional[str] = None
    order_date: Optional[datetime] = None
    file_name: str
    line_items: List[LineItem]
    created_at: datetime
    updated_at: datetime 