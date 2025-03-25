from fastapi import APIRouter, FastAPI, Depends, Request,  HTTPException, status, Request, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import JWTError

from conf.config import settings
from schemas.contact import ContactCreate, ContactResponse
from schemas.user import UserCreate, UserResponse, Token, UserLogin, UserBase
from services.contact import ContactService
from services.auth import Hash, create_access_token, get_email_from_token, get_current_user
from services.email import send_email
from services.users import UserService, UploadFileService
from database.db import get_db

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

auth_router = APIRouter(prefix="/auth", tags=["auth"])
contacts_router =  APIRouter(prefix="/contacts", tags=["contacts"])
users_router = APIRouter(prefix="/users", tags=["users"])

app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(users_router)

@users_router.get("/me", response_model=UserBase)
@limiter.limit("5/minute")
async def me(request: Request, user: UserBase = Depends(get_current_user)):
    return user


@users_router.patch("/avatar", response_model=UserBase)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user

@auth_router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
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
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
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
    contact_service = ContactService(db)
    return await contact_service.create_contact(contact)

@contacts_router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(skip=skip, limit=limit)

@contacts_router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_contact(contact_id)

@contacts_router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.update_contact(contact_id, contact)

@contacts_router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    await contact_service.remove_contact(contact_id)
    return {"message": "Contact deleted"}

@contacts_router.get("/contacts/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(days: int = 7, db: AsyncSession = Depends(get_db)):
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(days)
