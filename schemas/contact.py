from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date

    class Config:
        from_attributes = True  # Включення підтримки для model_validate

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    birth_date: Optional[date]

class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True  # Включення підтримки для model_validate