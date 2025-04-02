"""
Service for managing contact-related operations.

This module provides the `ContactService` class, which includes methods to create, 
retrieve, update, delete, and list contacts. Additionally, it offers functionality 
to find contacts with upcoming birthdays.

Classes:
    - ContactService: A service for managing contacts with CRUD operations and birthday reminders.

Methods:
    - create_contact: Creates a new contact, ensuring email and phone number uniqueness.
    - get_contacts: Retrieves a list of contacts filtered by name, surname, or email with pagination.
    - get_contact: Retrieves a specific contact by its ID.
    - update_contact: Updates an existing contact's details.
    - remove_contact: Deletes a contact from the database.
    - get_upcoming_birthdays: Retrieves contacts with birthdays within the specified number of days.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.models import Contact
from repository.contacts import ContactRepository
from schemas.contact import ContactCreate, ContactUpdate, ContactResponse

class ContactService:
    """
    Service to handle contact-related operations.

    This class provides methods to manage contacts, including creating, retrieving, 
    updating, deleting contacts, and retrieving contacts with upcoming birthdays.

    Attributes:
        repository (ContactRepository): A repository instance to interact with the database.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with the given database session.

        Args:
            db (AsyncSession): The asynchronous database session used for querying the database.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate) -> ContactResponse:
        """
        Create a new contact if the email and phone number are unique.

        This method checks whether a contact with the same email or phone number 
        already exists. If so, it raises an HTTPException with a 400 status code. 
        If not, it creates the new contact and returns a response containing the 
        created contact's data.

        Args:
            body (ContactCreate): The data used to create the new contact.

        Returns:
            ContactResponse: The response containing the newly created contact's data.

        Raises:
            HTTPException: If a contact with the same email or phone number already exists.
        """

        if await self.repository.is_contact_exists(body.email, body.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone_number}' phone number already exists."
            )

        new_contact = await self.repository.create_contact(body)
        return ContactResponse.model_validate(new_contact)

    async def get_contacts(self, name: str = '', surname: str = '', email: str = '', skip: int = 0, limit: int = 10) -> List[ContactResponse]:
        """
        Retrieve a list of contacts based on optional search filters.

        This method retrieves a list of contacts based on provided filters such as 
        name, surname, or email. Pagination is also supported through the `skip` 
        and `limit` parameters.

        Args:
            name (str, optional): The name of the contacts to search for (default is '').
            surname (str, optional): The surname of the contacts to search for (default is '').
            email (str, optional): The email of the contacts to search for (default is '').
            skip (int, optional): The number of records to skip (default is 0).
            limit (int, optional): The number of records to return (default is 10).

        Returns:
            List[ContactResponse]: A list of contacts that match the provided filters.
        """
        contacts = await self.repository.get_contacts(name, surname, email, skip, limit)
        return [ContactResponse.model_validate(contact) for contact in contacts]

    async def get_contact(self, contact_id: int) -> ContactResponse:
        """
        Retrieve a specific contact by its ID.

        This method fetches a contact from the database using its unique ID. 
        If the contact is not found, an HTTPException with a 404 status code is raised.

        Args:
            contact_id (int): The ID of the contact to retrieve.

        Returns:
            ContactResponse: The response containing the contact's data.

        Raises:
            HTTPException: If the contact with the specified ID is not found.
        """
        contact = await self.repository.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        return ContactResponse.model_validate(contact)

    async def update_contact(self, contact_id: int, body: ContactUpdate) -> ContactResponse:
        """
        Update an existing contact's information.

        This method updates a contact's information based on the provided contact ID 
        and the update data. It returns the updated contact data in the response.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The data to update the contact with.

        Returns:
            ContactResponse: The response containing the updated contact's data.
        """
        updated_contact = await self.repository.update_contact(contact_id, body)
        return ContactResponse.model_validate(updated_contact)

    async def remove_contact(self, contact_id: int) -> None:
        """
        Remove a contact from the database.

        This method deletes a contact from the database using its ID. 
        If the contact is not found, an HTTPException with a 404 status code is raised.

        Args:
            contact_id (int): The ID of the contact to remove.

        Raises:
            HTTPException: If the contact with the specified ID is not found.
        """
        contact = await self.repository.remove_contact(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )

    async def get_upcoming_birthdays(self, days: int = 7) -> List[ContactResponse]:
        """
        Retrieve a list of contacts with upcoming birthdays within a specified number of days.

        This method returns contacts that have birthdays in the upcoming `days` number 
        of days. The default value for `days` is 7.

        Args:
            days (int, optional): The number of days in the future to check for birthdays (default is 7).

        Returns:
            List[ContactResponse]: A list of contacts with upcoming birthdays within the specified period.
        """
        contacts = await self.repository.get_upcoming_birthdays(days)
        return [ContactResponse.model_validate(contact) for contact in contacts]
