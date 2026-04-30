from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field 
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(default=None, max_length=255)

class UserCreate(UserBase):
    model_config = ConfigDict(from_attributes=True)
    password: str
    age: Optional[int] = None

class UserUpdate(UserBase):
    model_config = ConfigDict(from_attributes=True)
    password: Optional[str] = None
    age: Optional[int] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    age: Optional[int]

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: Optional[int] = None

class MessageResponse(BaseModel):
    message: str