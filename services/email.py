"""
Email service for sending verification emails.

This module handles the creation and sending of verification emails using 
FastAPI Mail. It includes a method to send an email with a verification token 
to the user, allowing them to confirm their email address.

Functions:
    - send_email: Sends an email containing a verification link with a token for email confirmation.
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from services.auth import create_email_token
from conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send a verification email to the specified user.

    This function generates a verification token and sends an HTML email to 
    the provided email address. The email contains a confirmation link that 
    the user can use to verify their email.

    Args:
        email (EmailStr): The email address of the recipient.
        username (str): The username of the recipient to personalize the email.
        host (str): The host URL to be included in the email body for the verification link.

    Raises:
        ConnectionErrors: If there is an issue connecting to the email server.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
