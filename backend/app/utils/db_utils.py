import logging
from fastapi import Request
from contextlib import asynccontextmanager
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db_session(request: Request):
    """
    Context manager for MongoDB database access that handles errors.
    No longer using transactions as they're not supported on standalone MongoDB.
    """
    try:
        logger.info("Starting MongoDB database operation")
        # Get database
        db = request.app.mongodb
        # Just yield the database without session
        yield None, db
        logger.info("Completed MongoDB database operation")
    except PyMongoError as e:
        logger.error(f"MongoDB error: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise 