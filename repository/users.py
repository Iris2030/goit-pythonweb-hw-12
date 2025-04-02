"""
Repository for user-related database operations.

This module defines the `UserRepository` class, which includes methods for creating users, retrieving
users by email, ID, or username, and updating the user's avatar URL.

Methods:
    - create_user: Creates a new user with a hashed password.
    - get_user_by_email: Retrieves a user by their email address.
    - get_user_by_id: Retrieves a user by their ID.
    - get_user_by_username: Retrieves a user by their username.
    - update_avatar_url: Updates the avatar URL of a user.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import User
from schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    """
    Repository for user-related database operations.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserRepository.
        
        :param db: AsyncSession - SQLAlchemy async session instance
        """
        self.db = db

    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user with hashed password.
        
        :param user: UserCreate - User creation schema containing username, email, and password.
        :return: User - The newly created user object.
        """
        hashed_password = pwd_context.hash(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email.
        
        :param email: str - Email address of the user.
        :return: User | None - User object if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        
        :param user_id: int - The user's unique identifier.
        :return: User | None - User object if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.
        
        :param username: str - The user's username.
        :return: User | None - User object if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()
    
    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL of a user.
        
        :param email: str - The user's email address.
        :param url: str - New avatar URL.
        :return: User - Updated user object.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
        return user
