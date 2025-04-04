"""
Schemas for user-related operations using Pydantic.

This module defines various schemas for creating, updating, and managing user data, 
including login and authentication functionality.

Classes:
    - UserBase: Base schema for common user attributes (ID, username, email, avatar).
    - UserCreate: Schema for creating a new user (includes username, email, password).
    - UserResponse: Schema for returning full user data (includes creation timestamp and optional avatar).
    - UserLogin: Schema for user login requests (requires email and password).
    - Token: Schema for the response containing access token and token type after login.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """
    Base schema for user data.
    
    This model contains the core attributes that are common to all user-related
    operations. It is used as the foundation for creating, updating, and returning
    user data.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username chosen by the user.
        email (EmailStr): The email address of the user.
        avatar (str): A URL or path to the user's avatar image.
    """
    id: int
    username: str
    email: EmailStr
    avatar: str

class UserCreate(UserBase):
    """
    Schema for user creation.
    
    This model is used when creating a new user. It extends the `UserBase`
    schema and adds a `password` field. The `password` field is required 
    during the user creation process.

    Attributes:
        username (str): The desired username for the new user.
        email (str): The email address for the new user.
        password (str): The password for the new user.
    """
    id: int = 0 
    avatar: str = "default_avatar.jpg" 
    username: str
    email: str
    password: str


class UserResponse(UserBase):
    """
    Schema for the user response with extra details.
    
    This model extends the `UserBase` schema and is used when responding with
    a user's full data, including additional details such as creation time 
    and an optional avatar. It is typically used for returning user data 
    after a successful creation or fetch operation.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user (usually hashed).
        created_at (datetime): The timestamp of when the user was created.
        avatar (Optional[str]): An optional URL or path to the user's avatar image.
    """
    id: int
    username: str
    email: str
    password: str
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    This model is used to validate the data provided by the user when
    attempting to log in. It expects the user's email and password for authentication.

    Attributes:
        email (str): The email address of the user attempting to log in.
        password (str): The password provided by the user for authentication.
    """
    email: str
    password: str

class Token(BaseModel):
    """
    Schema for user login request.
    
    This model is used to validate the data provided by the user when
    attempting to log in. It expects the user's email and password for authentication.

    Attributes:
        email (str): The email address of the user attempting to log in.
        password (str): The password provided by the user for authentication.
    """
    access_token: str
    token_type: str