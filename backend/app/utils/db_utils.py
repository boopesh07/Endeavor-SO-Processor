import logging
from fastapi import Request
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db_session(request: Request):
    """
    Context manager for compatibility with MongoDB code.
    This is a simple wrapper that provides a mock session object.
    """
    try:
        logger.info("Using JSON storage instead of MongoDB session")
        # Create a dummy session and db object for compatibility
        session = None
        db = None
        yield session, db
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise 