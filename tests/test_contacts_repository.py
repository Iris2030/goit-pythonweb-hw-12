import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from models.models import Contact, User
from repository.contacts import ContactRepository
from schemas.contact import ContactCreate, ContactUpdate


@pytest.fixture
def mock_async_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_async_session):
    return ContactRepository(mock_async_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_async_session):
    contact_data = ContactCreate(
        first_name="Mia",
        last_name="Lee",
        email="mia@example.com",
        phone="+1234567890",
        birth_date="2000-01-01"
    )

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await contact_repository.create_contact(contact_data)

    assert isinstance(result, Contact)
    assert result.first_name == "Mia"
    assert result.last_name == "Lee"
    mock_async_session.add.assert_called_once()
    mock_async_session.commit.assert_awaited_once()
    mock_async_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_create_contact_with_existing_email(contact_repository, mock_async_session):
    contact_data = ContactCreate(
        first_name="Mia",
        last_name="Lee",
        email="mia@example.com",
        phone="+1234567890",
        birth_date="2000-01-01"
    )

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = Contact(id=1, email="mia@example.com")
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    with pytest.raises(ValueError):
        await contact_repository.create_contact(contact_data)


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_async_session):
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [Contact(id=1, first_name="Mia", last_name="Lee")]
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    contacts = await contact_repository.get_contacts(first_name="Mia", skip=0, limit=10)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Mia"
    assert contacts[0].last_name == "Lee"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_async_session):
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = Contact(id=1, first_name="Mia", last_name="Lee")
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1)

    assert contact is not None
    assert contact.first_name == "Mia"
    assert contact.last_name == "Lee"


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_async_session):
    contact_data = ContactUpdate(first_name="Updated Mia", last_name="Updated Lee")
    existing_contact = Contact(id=1, first_name="Mia", last_name="Lee")
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = existing_contact
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await contact_repository.update_contact(contact_id=1, contact=contact_data)

    assert result is not None
    assert result.first_name == "Updated Mia"
    assert result.last_name == "Updated Lee"
    mock_async_session.commit.assert_awaited_once()
    mock_async_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_update_contact_not_found(contact_repository, mock_async_session):
    contact_data = ContactUpdate(first_name="Updated Mia", last_name="Updated Lee")
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await contact_repository.update_contact(contact_id=1, contact=contact_data)

    assert result is None


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_async_session):
    existing_contact = Contact(id=1, first_name="Mia", last_name="Lee")
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = existing_contact
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

 
    await contact_repository.delete_contact(contact_id=1)
 
    mock_async_session.delete.assert_awaited_once_with(existing_contact)
    mock_async_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_repository, mock_async_session):
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    await contact_repository.delete_contact(contact_id=1)

    mock_async_session.delete.assert_not_awaited()
    mock_async_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contact_repository, mock_async_session):
    today = date.today()
    end_date = today + timedelta(days=7)
    contact_data = Contact(id=1, first_name="Mia", last_name="Lee", birth_date=today + timedelta(days=5))

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [contact_data]
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    contacts = await contact_repository.get_upcoming_birthdays(days=7)


    assert len(contacts) == 1
    assert contacts[0].first_name == "Mia"
    assert contacts[0].birth_date <= end_date
