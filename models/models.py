"""
SQLAlchemy models for contacts and users.

This module defines the `Contact` and `User` models for the database, using SQLAlchemy's ORM
to represent contacts and users. These models include basic attributes like names, emails, 
and creation timestamps, along with relationships for managing contact and user data.

Classes:
    - Contact: Represents a contact with personal details like name, email, phone, and birth date.
    - User: Represents a user with credentials, avatar, token, and verification status.
"""

from sqlalchemy import Column,Boolean, Integer, String, Date,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime

Base = declarative_base()

class Contact(Base):
    """
    Represents a contact in the database.
    
    Attributes:
        id: The primary key for the contact.
        first_name: The first name of the contact.
        last_name: The last name of the contact.
        email: The email address of the contact (unique).
        phone_number: The phone number of the contact.
        birth_date: The birth date of the contact.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birth_date = Column(Date)


class User(Base):
    """
    Represents a user in the database.
    
    Attributes:
        id: The primary key for the user.
        username: The unique username for the user.
        email: The unique email address of the user.
        hashed_password: The hashed password of the user.
        created_at: The creation timestamp of the user.
        avatar: The avatar URL for the user.
        token: The authentication token for the user.
        is_verified: Indicates if the user's email is verified.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    token = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)