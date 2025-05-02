from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Response
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json
from bson import ObjectId

from app.services.extraction_service import extract_from_pdf
from app.services.matching_service import match_single_item
from app.utils.db_utils import get_db_session
from app.services.sales_order_service import (
    create_sales_order, 
    match_sales_order_items, 
    update_sales_order,
    get_sales_order_csv
)
from app.utils.llm_utils import process_extracted_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function for JSON responses with ObjectId serialization
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def create_json_response(content: Any, status_code: int = 200):
    json_str = json.dumps(content, cls=JSONEncoder)
    return Response(
        content=json_str,
        media_type="application/json",
        status_code=status_code
    )

router = APIRouter(tags=["sales_orders"])

@router.post("/extract")
async def extract_from_sales_order(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Extract line items from a sales order PDF
    """
    try:
        # Extract line items from the PDF
        extracted_data = await extract_from_pdf(file)
        return create_json_response(extracted_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.post("/sales-orders")
async def create_new_sales_order(
    request: Request,
    file_name: str = Form(...),
    line_items: str = Form(...)
):
    """
    Create a new sales order in the database
    """
    try:
        # Parse the line items JSON
        line_items_data = json.loads(line_items)
        
        # Normalize field names in the extracted data
        normalized_items = []
        for item in line_items_data:
            normalized_item = {}
            
            # Copy Request Item field
            if "Request Item" in item:
                normalized_item["Request Item"] = item["Request Item"]
            
            # Normalize Quantity/Amount/Qty fields
            if "Quantity" in item:
                normalized_item["Quantity"] = item["Quantity"]
            elif "Qty" in item:
                normalized_item["Quantity"] = item["Qty"]
            elif "Amount" in item:
                normalized_item["Quantity"] = item["Amount"]
                normalized_item["Amount"] = item["Amount"]
            
            # Normalize Price/Unit Price fields
            if "Unit Price" in item:
                normalized_item["Unit Price"] = item["Unit Price"]
            elif "Price" in item:
                normalized_item["Unit Price"] = item["Price"]
            elif "Unit Cost" in item:
                normalized_item["Unit Price"] = item["Unit Cost"]
            
            # Copy Total field
            if "Total" in item:
                normalized_item["Total"] = item["Total"]
            elif "Amount" in item and "Quantity" in item and isinstance(item["Amount"], (int, float)) and item["Amount"] > item["Quantity"]:
                normalized_item["Total"] = item["Amount"]
            
            # Ensure matched_item and match_score fields exist (will be null)
            normalized_item["matched_item"] = item.get("matched_item")
            normalized_item["match_score"] = item.get("match_score")
            
            normalized_items.append(normalized_item)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Create the sales order
            sales_order = await create_sales_order(db, session, file_name, normalized_items)
            return create_json_response({"success": True, "sales_order_id": str(sales_order["_id"])})
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to create sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create sales order: {str(e)}")

@router.get("/sales-orders")
async def get_all_sales_orders(request: Request):
    """
    Get all sales orders
    """
    try:
        logger.info("Attempting to fetch all sales orders")
        
        # Check if MongoDB connection is available
        if not hasattr(request, 'app') or not hasattr(request.app, 'mongodb') or request.app.mongodb is None:
            logger.error("MongoDB connection not available")
            return create_json_response([], 200)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Get the MongoDB collection
            collection = db.sales_orders
            logger.info(f"Got collection: {collection}")
            
            # Get all sales orders (no session required now)
            sales_orders = await collection.find().to_list(length=100)
            logger.info(f"Found {len(sales_orders)} sales orders")
            
            return create_json_response(sales_orders)
            
    except Exception as e:
        logger.exception(f"Error fetching sales orders: {str(e)}")
        # Return empty list instead of error to handle case when no orders exist
        return create_json_response([], 200)

@router.get("/sales-orders/{sales_order_id}")
async def get_sales_order(request: Request, sales_order_id: str):
    """
    Get a specific sales order
    """
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(sales_order_id)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Get the sales order
            sales_order = await db.sales_orders.find_one({"_id": object_id})
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            return create_json_response(sales_order)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to get sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sales order: {str(e)}")

@router.post("/sales-orders/{sales_order_id}/match")
async def match_items(request: Request, sales_order_id: str):
    """
    Match all line items in a sales order
    """
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(sales_order_id)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Match the sales order items
            updated_sales_order = await match_sales_order_items(db, session, object_id)
            
            return create_json_response(updated_sales_order)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to match items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to match items: {str(e)}")

@router.get("/sales-orders/{sales_order_id}/match-item")
async def get_matches_for_item(request: Request, sales_order_id: str, item_name: str, limit: int = 5):
    """
    Get matches for a specific item
    """
    try:
        # Get matches for the item
        matches = await match_single_item(item_name, limit)
        
        return create_json_response(matches)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to get matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get matches: {str(e)}")

@router.patch("/sales-orders/{sales_order_id}")
async def update_order(
    request: Request,
    sales_order_id: str,
    updates: Dict[str, Any]
):
    """
    Update a sales order with new information
    """
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(sales_order_id)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Update the sales order
            updated_sales_order = await update_sales_order(db, session, object_id, updates)
            
            return create_json_response(updated_sales_order)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update sales order: {str(e)}")

@router.patch("/sales-orders/{sales_order_id}/line-items/{item_index}")
async def update_line_item(
    request: Request,
    sales_order_id: str,
    item_index: int,
    updates: Dict[str, Any]
):
    """
    Update a specific line item in a sales order
    """
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(sales_order_id)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Get the sales order
            sales_order = await db.sales_orders.find_one({"_id": object_id})
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            # Make sure the item index is valid
            if item_index < 0 or item_index >= len(sales_order["line_items"]):
                raise HTTPException(status_code=400, detail="Invalid line item index")
            
            # Update the line item
            update_query = {}
            for key, value in updates.items():
                update_query[f"line_items.{item_index}.{key}"] = value
            
            # Add updated timestamp
            update_query["updated_at"] = datetime.now()
            
            # Update the sales order
            await db.sales_orders.update_one(
                {"_id": object_id},
                {"$set": update_query}
            )
            
            # Get the updated sales order
            updated_sales_order = await db.sales_orders.find_one({"_id": object_id})
            
            return create_json_response(updated_sales_order)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update line item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update line item: {str(e)}")

@router.get("/sales-orders/{sales_order_id}/csv")
async def download_sales_order_csv(request: Request, sales_order_id: str):
    """
    Download a sales order as CSV
    """
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(sales_order_id)
        
        # Use DB session
        async with get_db_session(request) as (session, db):
            # Get the CSV content
            csv_content = await get_sales_order_csv(db, session, object_id)
            
            # Create a CSV response
            response = Response(content=csv_content)
            response.headers["Content-Disposition"] = f"attachment; filename=sales_order_{sales_order_id}.csv"
            response.headers["Content-Type"] = "text/csv"
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            return response
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to generate CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}") 