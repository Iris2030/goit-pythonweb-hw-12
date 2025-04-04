import pytest
from unittest import mock
from sqlalchemy.ext.asyncio import AsyncSession
from services import UserService, UploadFileService
from schemas.user import UserCreate
from repository.users import UserRepository

@pytest.fixture()
def mock_user_repo():
    with mock.patch.object(UserRepository, 'create_user', return_value=None) as mock_create_user, \
         mock.patch.object(UserRepository, 'get_user_by_email', return_value=None) as mock_get_user_by_email, \
         mock.patch.object(UserRepository, 'confirmed_email', return_value=None) as mock_confirmed_email, \
         mock.patch.object(UserRepository, 'update_avatar_url', return_value=None) as mock_update_avatar_url:
        yield {
            "create_user": mock_create_user,
            "get_user_by_email": mock_get_user_by_email,
            "confirmed_email": mock_confirmed_email,
            "update_avatar_url": mock_update_avatar_url,
        }


@pytest.mark.asyncio
async def test_create_user_with_gravatar(mock_user_repo):
    user_create_data = UserCreate(email="testuser@example.com", username="testuser", hashed_password="hashedpassword")

    with mock.patch('libgravatar.Gravatar.get_image', return_value="http://gravatar.com/testuser/avatar") as mock_gravatar:
        user_service = UserService(db=mock.Mock())
        await user_service.create_user(user_create_data)
        
        mock_gravatar.assert_called_once()
        mock_user_repo["create_user"].assert_called_once_with(user_create_data, "http://gravatar.com/testuser/avatar")


@pytest.mark.asyncio
async def test_create_user_without_gravatar(mock_user_repo):
    user_create_data = UserCreate(email="testuser@example.com", username="testuser", hashed_password="hashedpassword")

    with mock.patch('libgravatar.Gravatar.get_image', side_effect=Exception("Gravatar not found")):
        user_service = UserService(db=mock.Mock())
        await user_service.create_user(user_create_data)
        
        mock_user_repo["create_user"].assert_called_once_with(user_create_data, None)


@pytest.mark.asyncio
async def test_get_user_by_email(mock_user_repo):
    user_service = UserService(db=mock.Mock())
    mock_user_repo["get_user_by_email"].return_value = {"email": "testuser@example.com", "username": "testuser"}
    
    user = await user_service.get_user_by_email("testuser@example.com")
    
    mock_user_repo["get_user_by_email"].assert_called_once_with("testuser@example.com")
    assert user["email"] == "testuser@example.com"
    assert user["username"] == "testuser"

@pytest.mark.asyncio
async def test_upload_file():

    with mock.patch('cloudinary.uploader.upload', return_value={"version": 123, "public_id": "RestApp/testuser"}) as mock_upload:
        upload_service = UploadFileService(cloud_name="mycloud", api_key="apikey", api_secret="apisecret")
        file_mock = mock.Mock()  
        file_mock.file = "file_content"
        
        src_url = upload_service.upload_file(file_mock, "testuser")       
 
        mock_upload.assert_called_once_with(file_mock.file, public_id="RestApp/testuser", overwrite=True)
        
        expected_url = "https://res.cloudinary.com/mycloud/image/upload/v123/RestApp/testuser.png?w=250&h=250&crop=fill"
        assert src_url == expected_url
