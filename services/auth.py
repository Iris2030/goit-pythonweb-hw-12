"""
OAuth2 and JWT authentication utilities.

This module provides functions and classes for password hashing, JWT token 
generation, and user authentication using FastAPI.

Classes:
    - Hash: Handles password hashing and verification with bcrypt.
    
Functions:
    - create_access_token: Generates a JWT access token with optional expiration.
    - get_current_user: Decodes JWT token and retrieves user from the database.
    - get_email_from_token: Extracts email from the provided JWT token.
    - create_email_token: Generates a JWT for email verification with a 1-week expiration.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database.db import get_db
from conf.config import settings
from services.users import UserService


class Hash:
    """
    Class to handle password hashing and verification.
    
    This class provides methods for securely hashing passwords and verifying
    a plain password against a hashed one using the bcrypt hashing algorithm.

    Methods:
        verify_password(plain_password: str, hashed_password: str) -> bool:
            Verifies if the plain password matches the hashed password.
        
        get_password_hash(password: str) -> str:
            Hashes a given password using bcrypt.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify if the plain password matches the hashed password.
        
        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare with.
        
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a given password using bcrypt.
        
        Args:
            password (str): The plain password to hash.
        
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create an access token with expiration.
    
    This function generates a JSON Web Token (JWT) for the user, embedding the
    provided data (usually user info), and includes an expiration time. If no
    expiration time is provided, a default expiration is applied.

    Args:
        data (dict): The data to encode into the JWT (e.g., user information).
        expires_delta (Optional[int]): The number of seconds before the token expires.
        
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Get the current user based on the provided token.
    
    This function decodes the provided JWT token, extracts the username, and 
    fetches the corresponding user from the database. If the token is invalid or 
    the user cannot be found, an exception is raised.

    Args:
        token (HTTPAuthorizationCredentials): The authorization credentials, typically a JWT.
        db (Session): The database session used to fetch the user data.
        
    Returns:
        User: The user object associated with the decoded token.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


async def get_email_from_token(token: str):
    """
    Extract the email from the provided token.
    
    This function decodes the JWT token and extracts the email address embedded 
    within the token. If the token is invalid, an exception is raised.

    Args:
        token (str): The JWT token containing the user's email.
        
    Returns:
        str: The email address encoded in the token.
    
    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Невірний токен для перевірки електронної пошти",
        )
    
def create_email_token(data: dict):
    """
    Create an email verification token.
    
    This function generates a JWT token for email verification purposes. The token
    includes a one-week expiration time and is encoded with the provided user data.

    Args:
        data (dict): The data to encode into the token, typically user information.
        
    Returns:
        str: The generated email verification token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token