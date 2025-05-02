from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import sales_orders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MongoDBCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not hasattr(request.app, "mongodb") or request.app.mongodb is None:
            logger.error("MongoDB connection not available")
            # Still proceed to let the route handler handle the error gracefully
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception(f"Unhandled exception in middleware: {str(e)}")
            # Create a custom error response
            return Response(
                content=f"Internal Server Error: {str(e)}",
                status_code=500
            )

app = FastAPI(title="Sales Order Processor")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add MongoDB check middleware
app.add_middleware(MongoDBCheckMiddleware)

# MongoDB connection
@app.on_event("startup")
async def startup_db_client():
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        app.mongodb_client = AsyncIOMotorClient(mongodb_uri)
        app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB", "sales_orders_db")]
        
        # Test the connection
        await app.mongodb.command("ping")
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        # Still set the client to allow the app to start
        app.mongodb_client = None
        app.mongodb = None

@app.on_event("shutdown")
async def shutdown_db_client():
    if app.mongodb_client:
        app.mongodb_client.close()
        logger.info("MongoDB connection closed")

# Include routers
app.include_router(sales_orders.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Sales Order Processing API"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the application and database are running
    """
    health = {
        "status": "healthy",
        "mongodb": False
    }
    
    if app.mongodb_client:
        try:
            # Check if MongoDB is responding
            await app.mongodb.command("ping")
            health["mongodb"] = True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            health["status"] = "unhealthy"
            health["error"] = str(e)
    else:
        health["status"] = "unhealthy"
        health["error"] = "MongoDB client not initialized"
        
    return health 