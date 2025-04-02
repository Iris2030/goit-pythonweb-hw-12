"""
Repository class for managing contacts in the database.

This module defines the `ContactRepository` class, which includes methods for creating, retrieving,
updating, and deleting contacts. It also provides functionality to fetch contacts with upcoming birthdays.

Methods:
    - create_contact: Creates a new contact in the database.
    - get_contacts: Retrieves a list of contacts with optional filters.
    - get_contact_by_id: Retrieves a contact by its ID.
    - update_contact: Updates an existing contact.
    - delete_contact: Deletes a contact by its ID.
    - get_upcoming_birthdays: Retrieves contacts with upcoming birthdays within a specified number of days.
"""

from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Contact
from schemas.contact import ContactCreate, ContactUpdate


class ContactRepository:
    """
    Repository class for managing contacts in the database.
    
    Attributes:
        db: The database session to perform operations.
    """
    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactRepository with a database session.
        
        Args:
            db (AsyncSession): The database session.
        """
        self.db = db

    async def create_contact(self, contact: ContactCreate) -> Contact:
        """
        Creates a new contact in the database.
        
        Args:
            contact (ContactCreate): The contact information to create.
        
        Raises:
            ValueError: If a contact with the same email already exists.
        
        Returns:
            Contact: The created contact.
        """
        existing_contact = await self.db.execute(
            select(Contact).where(Contact.email == contact.email)
        )
        if existing_contact.scalar_one_or_none():
            raise ValueError(f"Contact with email {contact.email} already exists")

        db_contact = Contact(**contact.model_dump(exclude_unset=True))
        self.db.add(db_contact)
        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def get_contacts(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Contact]:
        """
        Retrieves a list of contacts based on provided filters.
        
        Args:
            first_name (Optional[str]): Filter by first name.
            last_name (Optional[str]): Filter by last name.
            email (Optional[str]): Filter by email.
            skip (int): Number of contacts to skip.
            limit (int): Number of contacts to return.
        
        Returns:
            List[Contact]: A list of contacts matching the filters.
        """
        query = select(Contact)
        filters = []

        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))

        if filters:
            query = query.where(or_(*filters))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """
        Retrieves a contact by its ID.
        
        Args:
            contact_id (int): The ID of the contact to retrieve.
        
        Returns:
            Optional[Contact]: The contact if found, otherwise None.
        """
        result = await self.db.execute(select(Contact).filter_by(id=contact_id))
        return result.scalar_one_or_none()

    async def update_contact(
        self, contact_id: int, contact: ContactUpdate
    ) -> Optional[Contact]:
        """
        Updates an existing contact's information.
        
        Args:
            contact_id (int): The ID of the contact to update.
            contact (ContactUpdate): The updated contact data.
        
        Returns:
            Optional[Contact]: The updated contact if successful, otherwise None.
        """
        db_contact = await self.get_contact_by_id(contact_id)
        if not db_contact:
            return None

        update_data = contact.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)

        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def delete_contact(self, contact_id: int) -> None:
        """
        Deletes a contact by its ID.
        
        Args:
            contact_id (int): The ID of the contact to delete.
        """
        db_contact = await self.get_contact_by_id(contact_id)
        if db_contact:
            await self.db.delete(db_contact)
            await self.db.commit()

    async def get_upcoming_birthdays(self, days: int) -> List[Contact]:
        """
        Retrieves contacts with upcoming birthdays within the specified number of days.
        
        Args:
            days (int): The number of days to check for upcoming birthdays.
        
        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = date.today()
        end_date = today + timedelta(days=days)

        query = (
            select(Contact)
            .where(
                and_(
                    Contact.birth_date >= today,
                    Contact.birth_date <= end_date,
                )
            )
            .order_by(Contact.birth_date.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()
