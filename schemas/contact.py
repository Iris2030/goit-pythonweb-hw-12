"""
Schemas for contact-related operations using Pydantic.

This module defines various schemas for creating, updating, and returning contact data. 
It includes base and specialized schemas for different contact operations.

Classes:
    - ContactBase: Base schema for common contact attributes (first name, last name, email, phone number, birth date).
    - ContactCreate: Schema for creating a new contact (inherits from `ContactBase`).
    - ContactUpdate: Schema for updating an existing contact (all fields are optional).
    - ContactResponse: Schema for returning contact data (includes ID field).
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    """
    Base schema for contact-related operations.
    
    This model contains the common attributes for contacts. It is used
    as a base for creating, updating, and returning contact data.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birth_date (date): The birth date of the contact.
    """
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None  
    birth_date: Optional[date] = None 

    class Config:
        from_attributes = True   

class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    
    Inherits from `ContactBase` and is used to define the structure
    for creating new contacts. It validates the required fields for 
    creating a contact but does not include any contact ID since the 
    ID is typically auto-generated.
    """
    pass

class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.
    
    This model allows optional updates to the attributes of an existing
    contact. Only the fields that are provided will be updated.

    Attributes:
        first_name (Optional[str]): The first name of the contact (optional).
        last_name (Optional[str]): The last name of the contact (optional).
        email (Optional[str]): The email address of the contact (optional).
        phone_number (Optional[str]): The phone number of the contact (optional).
        birth_date (Optional[date]): The birth date of the contact (optional).
    """
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    birth_date: Optional[date]

class ContactResponse(ContactBase):
    """
    Schema for the response that includes the contact data.
    
    This model inherits from `ContactBase` and adds an ID field. It is
    used when returning contact data, typically after creation or when
    retrieving a specific contact.

    Attributes:
        id (int): The unique identifier of the contact.
    """
    id: int

    class Config:
        from_attributes = True   