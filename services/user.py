"""
User service and file upload handling.

This module contains services for managing user-related operations, such as user creation, 
retrieving user details, updating avatars, and confirming email addresses. It also handles 
file uploads, specifically managing user avatars on Cloudinary.

Classes:
    - UserService: Manages user creation, retrieval, and avatar update operations, 
                  including optional Gravatar fetching.
    - UploadFileService: Handles file uploads to Cloudinary, specifically for user avatars.
""" 

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader

from repository.users import UserRepository
from schemas.user import UserCreate

class UserService:
    """
    Service to handle user-related operations, such as creating a user, 
    retrieving user details, and updating user data.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a repository for user operations.

        Args:
            db (AsyncSession): The database session to interact with the database.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user in the system, optionally fetching a Gravatar image.

        Args:
            body (UserCreate): The user creation data, including email.

        Returns:
            The created user record, including the generated avatar URL.
        
        If the user does not provide an avatar, a Gravatar is generated using
        the user's email. If the Gravatar cannot be fetched, the user is created
        without an avatar.
        """
        avatar = None
        try:
            # Attempt to fetch the Gravatar image for the user
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            # Log any errors encountered while fetching Gravatar
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The unique ID of the user.

        Returns:
            User: The user record retrieved from the database.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User: The user record retrieved from the database.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email of the user.

        Returns:
            User: The user record retrieved from the database.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        Args:
            email (str): The email of the user to be confirmed.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        Args:
            email (str): The email of the user.
            url (str): The new avatar URL.
        
        Returns:
            User: The updated user record with the new avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)

class UploadFileService:
    """
    Service to handle file uploads, specifically for managing user avatars 
    on Cloudinary.
    """
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the UploadFileService with Cloudinary credentials.

        Args:
            cloud_name (str): The Cloudinary cloud name.
            api_key (str): The Cloudinary API key.
            api_secret (str): The Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file (e.g., user avatar) to Cloudinary and return the public URL.

        Args:
            file (file): The file to be uploaded (e.g., an image file).
            username (str): The username of the user to associate with the uploaded file.

        Returns:
            str: The URL of the uploaded file.
        
        The uploaded file is stored with a public ID based on the username and 
        a fixed folder path in Cloudinary. The URL returned is optimized for a 
        250x250 square avatar.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        # Build the URL with specific image size (250x250)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
