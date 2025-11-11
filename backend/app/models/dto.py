from datetime import date
from typing import Annotated, List
from pydantic import BaseModel, ConfigDict

# Request DTO: what the client sends when creating a user
class UserCreateRequest(BaseModel):
    clerk_user_id: str
    first_name: str
    last_name: str
    email: str

# Response DTO: what you send back to the client after creating a user
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    clerk_user_id: str
    first_name: str
    last_name: str
    email: str
    currently_staying: bool


# Pricing DTOs
class PricingRequest(BaseModel):
    hotel_id: int
    room_type_code: str
    from_: date  # use from_ to avoid Python keyword
    to: date


class PricingItem(BaseModel):
    date: str
    room_type_code: str
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str] = []


class PricingResponse(BaseModel):
    items: List[PricingItem]
    modelVersion: str
