from sqlalchemy import Column, Boolean, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import Enum  # використовуємо Enum з SQLAlchemy
from enum import Enum as PyEnum  # для власних перерахувань

Base = declarative_base()

class UserRole(PyEnum):
    """
    Enum representing the roles of a user.
    """
    ADMIN = "admin"
    USER = "user"

class Contact(Base):
    """
    Represents a contact in the database.
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
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    avatar = Column(String(255), nullable=True)
    token = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(
        Enum(UserRole, create_type=True),  
        name="role",
        default=UserRole.USER,  
        nullable=False,
    )

class PasswordResetToken(Base):
    """
    Represents a token used for resetting the password.
    """
    __tablename__ = 'password_reset_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship('User', backref='password_reset_tokens')

    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at
