import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import PasswordResetToken, User
from passlib.context import CryptContext

expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordResetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(self, user: User):
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(reset_token)
        await self.db.commit()
        return token

    async def verify_token(self, token: str):
        result = await self.db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        reset_token = result.scalar_one_or_none()
        if not reset_token or reset_token.is_expired():
            return None
        return reset_token

    async def reset_password(self, token: str, new_password: str):
        reset_token = await self.verify_token(token)
        if not reset_token:
            return None

        result = await self.db.execute(
            select(User).where(User.id == reset_token.user_id)
        )
        user = result.scalar_one()
        user.hashed_password = pwd_context.hash(new_password)

     
        await self.db.delete(reset_token)
        await self.db.commit()
        return user
