from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.models import Contact
from repository.contacts import ContactRepository
from schemas.contact import ContactCreate, ContactUpdate, ContactResponse

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate) -> ContactResponse:
        if await self.repository.is_contact_exists(body.email, body.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone_number}' phone number already exists."
            )

        new_contact = await self.repository.create_contact(body)
        return ContactResponse.model_validate(new_contact)

    async def get_contacts(self, name: str = '', surname: str = '', email: str = '', skip: int = 0, limit: int = 10) -> List[ContactResponse]:
        contacts = await self.repository.get_contacts(name, surname, email, skip, limit)
        return [ContactResponse.model_validate(contact) for contact in contacts]

    async def get_contact(self, contact_id: int) -> ContactResponse:
        contact = await self.repository.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        return ContactResponse.model_validate(contact)

    async def update_contact(self, contact_id: int, body: ContactUpdate) -> ContactResponse:
        updated_contact = await self.repository.update_contact(contact_id, body)
        return ContactResponse.model_validate(updated_contact)

    async def remove_contact(self, contact_id: int) -> None:
        contact = await self.repository.remove_contact(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )

    async def get_upcoming_birthdays(self, days: int = 7) -> List[ContactResponse]:
        contacts = await self.repository.get_upcoming_birthdays(days)
        return [ContactResponse.model_validate(contact) for contact in contacts]
