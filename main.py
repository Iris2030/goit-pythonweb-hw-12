from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from schemas.contact import ContactCreate, ContactResponse
from services.contact import ContactService
from database.db import get_db

app = FastAPI()

@app.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.create_contact(contact)

@app.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(skip=skip, limit=limit)

@app.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_contact(contact_id)

@app.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.update_contact(contact_id, contact)

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    await contact_service.remove_contact(contact_id)
    return {"message": "Contact deleted"}

@app.get("/contacts/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(days: int = 7, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(days)
