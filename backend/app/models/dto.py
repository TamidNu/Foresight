from typing import Annotated
from pydantic import BaseModel, ConfigDict
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
