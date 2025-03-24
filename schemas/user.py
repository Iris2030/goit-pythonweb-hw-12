from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

class UserCreate(UserBase):
    username: str
    email: str
    password: str


class UserResponse(UserBase):
    id: int
    username: str
    email: str
    password: str
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str