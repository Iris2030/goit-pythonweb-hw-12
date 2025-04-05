"""
FastAPI application entry point.

This module initializes the FastAPI app and includes routes for user authentication, 
profile management, and contact management. It also configures rate limiting for requests.

Functions:
    - rate_limit_handler: Handles rate limit exceeded errors with a custom message.
"""

from fastapi import APIRouter, FastAPI, Depends, Request, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import JWTError,jwt
import json
import redis.asyncio as redis

from conf.config import settings
from schemas.contact import ContactCreate, ContactResponse
from schemas.user import UserCreate, UserResponse, Token, UserLogin, UserBase
from services.contact import ContactService
from services.auth import Hash, create_access_token, get_email_from_token, get_current_user,create_refresh_token, get_current_admin_user
from services.email import send_email
from services.user import UserService, UploadFileService
from database.db import get_db
from database.redis import get_redis
from services.password_reset import PasswordResetService

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

auth_router = APIRouter(prefix="/auth", tags=["auth"])
contacts_router = APIRouter(prefix="/contacts", tags=["contacts"])
users_router = APIRouter(prefix="/users", tags=["users"])
password_router = APIRouter(prefix="/password-reset", tags=["users"])
from schemas.password_reset import PasswordResetRequest, PasswordResetConfirm

app.include_router(auth_router, prefix="/api")
app.include_router(contacts_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(password_router, prefix="/api")


@users_router.get("/me", response_model=UserBase)
@limiter.limit("5/minute")
async def me(request: Request, user: UserBase = Depends(get_current_user)):
    """
    Retrieve the current authenticated user.

    Args:
        request (Request): The FastAPI request object.
        user (UserBase, optional): The current authenticated user, retrieved from the `get_current_user` dependency.

    Returns:
        UserBase: The current user's details.
    """
    return user

@password_router.post("/request")
async def request_password_reset(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiates the password reset process by generating a reset token and sending it via email.

    Args:
        body (PasswordResetRequest): The request body containing the user's email.
        background_tasks (BackgroundTasks): FastAPI background task manager.
        db (AsyncSession): The database session.

    Raises:
        HTTPException: If the user with the provided email is not found.

    Returns:
        dict: A success message.
    """
    
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    token = await PasswordResetService(db).create_reset_token(user)

    background_tasks.add_task(send_email, user.email, token)

    return {"message": "Password reset instructions have been sent to your email."}

@password_router.post("/confirm")
async def confirm_password_reset(body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    """
    Confirms the password reset by validating the token and setting the new password.

    Args:
        body (PasswordResetConfirm): The request body containing the reset token and new password.
        db (AsyncSession): The database session.

    Raises:
        HTTPException: If the token is invalid or has expired.

    Returns:
        dict: A success message indicating that the password has been successfully reset.
    """
    service = PasswordResetService(db)
    user = await service.reset_password(body.token, body.new_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    return {"message": "Password successfully reset"}


@users_router.patch("/avatar", response_model=UserBase)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserBase = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the user's avatar.

    Args:
        file (UploadFile): The avatar image file.
        user (UserBase): The current authenticated user.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        UserBase: The updated user with the new avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user

@auth_router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Register a new user in the system.

    Args:
        user_data (UserCreate): The data for the user to be registered.
        request (Request): The FastAPI request object.
        background_tasks (BackgroundTasks): A background task manager for sending confirmation emails.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        UserResponse: The details of the newly created user.
    
    Raises:
        HTTPException: If the email or username is already taken.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user

@auth_router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis)):
    """
    Log a user into the system and return an access token.

    Args:
        body (UserLogin): The login credentials (email and password).
        db (Session): The database session to query user data.

    Returns:
        Token: The access token for the user.

    Raises:
        HTTPException: If the login credentials are incorrect.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    
    cached_user = await redis.get(f"user:{user.username}")
    if cached_user:
        user = json.loads(cached_user)   
   
    if not user or not Hash().verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await create_access_token(data={"sub": user["username"]})
    refresh_token = await create_refresh_token(data={"sub": user["username"]})

    await redis.set(f"user:{user['username']}", json.dumps(user), ex=3600)  

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token,  settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
       
        user = await UserService.get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
@auth_router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address by verifying the token.

    Args:
        token (str): The token used to confirm the email address.
        db (Session): The database session to interact with the database.

    Returns:
        dict: A message indicating the result of the email confirmation.
    
    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}

@auth_router.post("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify the user's email using the provided token.

    Args:
        token (str): The token used for email verification.
        db (Session): The database session to interact with the database.

    Returns:
        dict: A message indicating the result of the email verification.
    
    Raises:
        HTTPException: If the token is invalid, the user is not found, or the email is already verified.
    """
    try:
        email = await get_email_from_token(token)   
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний токен для перевірки електронної пошти"
        )

    user = await UserService(db).get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    user.is_verified = True   
    db.commit()
    db.refresh(user)
    return {"message": "Email successfully verified"}

@contacts_router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new contact.

    Args:
        contact (ContactCreate): The contact data to be created.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        ContactResponse: The details of the created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(contact)

@contacts_router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of contacts.

    Args:
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return (for pagination).
        db (AsyncSession): The database session to interact with the database.

    Returns:
        List[ContactResponse]: A list of contact details.
    """
    contact_service = ContactService(db)
    return await contact_service.get_contacts(skip=skip, limit=limit)

@contacts_router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single contact by its ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        ContactResponse: The contact details for the specified ID.
    """
    contact_service = ContactService(db)
    return await contact_service.get_contact(contact_id)

@contacts_router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    """
    Update an existing contact's details.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (ContactCreate): The updated contact data.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        ContactResponse: The updated contact details.
    """
    contact_service = ContactService(db)
    return await contact_service.update_contact(contact_id, contact)

@contacts_router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a contact by its ID.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session to interact with the database.

    Returns:
        dict: A message indicating that the contact has been deleted.
    """
    contact_service = ContactService(db)
    await contact_service.remove_contact(contact_id)
    return {"message": "Contact deleted"}

@contacts_router.get("/contacts/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of contacts with upcoming birthdays.

    Args:
        db (AsyncSession): The database session to interact with the database.

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays()
