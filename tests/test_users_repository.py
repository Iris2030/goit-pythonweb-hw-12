import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User
from repository.users import UserRepository
from schemas import UserCreate


@pytest.fixture
def mock_async_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_async_session):
    return UserRepository(mock_async_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com", confirmed=False, role="ADMIN")


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_async_session, user):

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = user
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await user_repository.get_user_by_id(user_id=1)

    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_async_session, user):

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = user
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await user_repository.get_user_by_username(username="testuser")

    assert result is not None
    assert result.username == "testuser"
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_async_session, user):

    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = user
    mock_async_session.execute = AsyncMock(return_value=mock_execute_result)

    result = await user_repository.get_user_by_email(email="test@example.com")

    assert result is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_async_session):
 
    user_data = UserCreate(
        username="newtestuser",
        email="newtestuser@example.com",
        password="newpassword",
        role="ADMIN"
    )

    result = await user_repository.create_user(body=user_data, avatar="http://example.com/avatar.png")

    assert isinstance(result, User)
    assert result.username == "newtestuser"
    assert result.email == "newtestuser@example.com"
    assert result.avatar == "http://example.com/avatar.png"
    mock_async_session.add.assert_called_once()
    mock_async_session.commit.assert_awaited_once()
    mock_async_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_email():
    mock_async_session = AsyncMock()
    repo = UserRepository(mock_async_session)

    mock_user = User(email="test@example.com", confirmed=False, role="ADMIN")
    repo.get_user_by_email = AsyncMock(return_value=mock_user)

    await repo.confirmed_email("test@example.com")

    assert mock_user.confirmed is True
    mock_async_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_avatar_url():
    mock_async_session = AsyncMock()
    repo = UserRepository(mock_async_session)

    mock_user = User(email="test@example.com", avatar="old_url", role="ADMIN")
    repo.get_user_by_email = AsyncMock(return_value=mock_user)

    updated_user = await repo.update_avatar_url("test@example.com", "new_url")

    assert updated_user.avatar == "new_url"
    mock_async_session.commit.assert_awaited()
    mock_async_session.refresh.assert_awaited_with(mock_user)
