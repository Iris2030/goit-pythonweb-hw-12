"""
Configuration settings for the application.

This module defines a `Settings` class using Pydantic to load and manage environment variables,
which include database credentials, JWT settings, email server configurations, and cloud service keys.

Attributes:
    - DB_URL: Database connection URL.
    - JWT_SECRET: Secret key for signing JWT tokens.
    - MAIL_USERNAME: Username for the mail server.
    - CLD_API_KEY: API key for cloud storage.
"""

from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class to hold configuration variables for the application.
    
    Attributes:
        DB_URL: The database connection URL.
        JWT_SECRET: The secret key used to sign JWT tokens.
        JWT_ALGORITHM: The algorithm used to sign JWT tokens. Defaults to "HS256".
        JWT_EXPIRATION_SECONDS: Expiration time of JWT tokens in seconds. Defaults to 3600.
        MAIL_USERNAME: The username for the mail server.
        MAIL_PASSWORD: The password for the mail server.
        MAIL_FROM: The email address used as the sender.
        MAIL_PORT: The port number for the mail server.
        MAIL_SERVER: The mail server URL.
        MAIL_FROM_NAME: The name associated with the email address.
        MAIL_STARTTLS: Whether to use TLS encryption for email. Defaults to False.
        MAIL_SSL_TLS: Whether to use SSL/TLS for email. Defaults to True.
        USE_CREDENTIALS: Whether to use credentials for the mail server. Defaults to True.
        VALIDATE_CERTS: Whether to validate SSL certificates. Defaults to True.
        TEMPLATE_FOLDER: The folder where email templates are stored.
        CLD_NAME: Cloud service name for storing media.
        CLD_API_KEY: API key for the cloud service.
        CLD_API_SECRET: API secret for the cloud service.
    """
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / "services" / "templates"

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
