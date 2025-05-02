from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import sales_orders
from app.utils.json_storage import ensure_storage_dir

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
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

# Add request middleware
app.add_middleware(RequestMiddleware)

# JSON storage initialization
@app.on_event("startup")
async def startup_storage():
    try:
        # Ensure storage directory exists
        ensure_storage_dir()
        logger.info("JSON storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize JSON storage: {str(e)}")

# Include routers
app.include_router(sales_orders.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Sales Order Processing API"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the application is running
    """
    return {
        "status": "healthy",
        "storage": "JSON"
    } 