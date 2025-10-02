from typing import Annotated
from pydantic import BaseModel, ConfigDict

# Request DTO: what the client sends when creating a user
class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    phone_number: int

# Response DTO: what you send back to the client after creating a user
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    phone_number: int
    currently_staying: bool
