"""
Database session management for asynchronous operations.

This module provides a `DatabaseSessionManager` class that manages the lifecycle of SQLAlchemy
sessions for asynchronous database interactions. It includes a context manager to handle sessions
and ensure proper handling of commits, rollbacks, and session closures.

Attributes:
    - _engine: The SQLAlchemy async engine for creating database connections.
    - _session_maker: The session maker used to create sessions.
    
Functions:
    - get_db: Yields a database session for async operations.
"""

import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

DB_URL = "postgresql+asyncpg://postgres:12345@localhost:5434/contacts"

class DatabaseSessionManager:
    """
    Manages database sessions for asynchronous operations.
    
    Attributes:
        _engine: The SQLAlchemy async engine for creating database connections.
        _session_maker: The session maker used to create sessions.
    """
    def __init__(self, url: str):
        """
        Initializes the DatabaseSessionManager with the database URL.
        
        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url, echo=True)
        
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides a context manager for database sessions.
        
        Yields:
            session: The database session.
            
        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If an error occurs during the session operation.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        
        session = self._session_maker()
        try:
            yield session   
        except SQLAlchemyError as e:
            await session.rollback()  
            raise  
        finally:
            await session.close()  

sessionmanager = DatabaseSessionManager(DB_URL)

async def get_db():
    """
    Yields a database session for async operations.
    
    Yields:
        session: The database session.
    """
    async with sessionmanager.session() as session:
        yield session
