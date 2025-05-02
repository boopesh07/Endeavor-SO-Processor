from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Response
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

from app.services.extraction_service import extract_from_pdf
from app.services.matching_service import match_single_item
from app.utils.db_utils import get_db_session
from app.utils.json_storage import (
    create_sales_order as json_create_order,
    get_sales_orders,
    get_sales_order_by_id,
    update_sales_order as json_update_order,
    update_line_item,
    DateTimeEncoder
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["sales_orders"])

# Helper function to create JSON response with datetime support
def create_json_response(content: Any, status_code: int = 200):
    json_str = json.dumps(content, cls=DateTimeEncoder)
    return Response(
        content=json_str,
        media_type="application/json",
        status_code=status_code
    )

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
    Create a new sales order in the JSON storage
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
            
            # Copy Total field
            if "Total" in item:
                normalized_item["Total"] = item["Total"]
            
            # Ensure matched_item and match_score fields exist (will be null)
            normalized_item["matched_item"] = item.get("matched_item")
            normalized_item["match_score"] = item.get("match_score")
            
            normalized_items.append(normalized_item)
        
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Create the sales order using JSON storage
            sales_order = json_create_order(file_name, normalized_items)
            return create_json_response({"success": True, "sales_order_id": sales_order["_id"]})
            
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
        logger.info("Fetching all sales orders from JSON storage")
        
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Get all sales orders from JSON storage
            sales_orders = get_sales_orders()
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
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Get the sales order from JSON storage
            sales_order = get_sales_order_by_id(sales_order_id)
            
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
    Match all line items in a sales order (dummy implementation for now)
    """
    try:
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Get the sales order
            sales_order = get_sales_order_by_id(sales_order_id)
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            # Update status
            updated_sales_order = json_update_order(sales_order_id, {"status": "matched"})
            
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
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Check if the sales order exists
            sales_order = get_sales_order_by_id(sales_order_id)
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            # Update the sales order
            updated_sales_order = json_update_order(sales_order_id, updates)
            
            return create_json_response(updated_sales_order)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update sales order: {str(e)}")

@router.patch("/sales-orders/{sales_order_id}/line-items/{item_index}")
async def update_line_item_endpoint(
    request: Request,
    sales_order_id: str,
    item_index: int,
    updates: Dict[str, Any]
):
    """
    Update a specific line item in a sales order
    """
    try:
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Check if the sales order exists
            sales_order = get_sales_order_by_id(sales_order_id)
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            # Update the line item
            try:
                updated_sales_order = update_line_item(sales_order_id, item_index, updates)
                return create_json_response(updated_sales_order)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to update line item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update line item: {str(e)}")

@router.get("/sales-orders/{sales_order_id}/csv")
async def download_sales_order_csv(request: Request, sales_order_id: str):
    """
    Generate CSV for a sales order
    """
    try:
        # Use DB session for compatibility
        async with get_db_session(request) as (session, db):
            # Get the sales order
            sales_order = get_sales_order_by_id(sales_order_id)
            
            if not sales_order:
                raise HTTPException(status_code=404, detail="Sales order not found")
            
            # Generate CSV content
            csv_content = "Request Item,Matched Product,Quantity,Unit Price,Total\n"
            
            for item in sales_order["line_items"]:
                # Get values with proper handling of None values and different field names
                request_item = str(item.get("Request Item", "")) if item.get("Request Item") is not None else ""
                matched_item = str(item.get("matched_item", "")) if item.get("matched_item") is not None else ""
                
                # Get quantity from any of the possible fields
                quantity = ""
                if item.get("Quantity") is not None:
                    quantity = str(item.get("Quantity"))
                elif item.get("Qty") is not None:
                    quantity = str(item.get("Qty"))
                elif item.get("Amount") is not None:
                    quantity = str(item.get("Amount"))
                
                # Get unit price from any of the possible fields
                unit_price = ""
                if item.get("Unit Price") is not None:
                    try:
                        unit_price = f"{float(item['Unit Price']):.2f}"
                    except (ValueError, TypeError):
                        unit_price = str(item["Unit Price"])
                elif item.get("Price") is not None:
                    try:
                        unit_price = f"{float(item['Price']):.2f}"
                    except (ValueError, TypeError):
                        unit_price = str(item["Price"])
                
                # Get total
                total = ""
                if item.get("Total") is not None:
                    try:
                        total = f"{float(item['Total']):.2f}"
                    except (ValueError, TypeError):
                        total = str(item["Total"])
                
                # Escape commas and quotes in text fields
                request_item = f'"{request_item.replace("\"", "\"\"")}"' if "," in request_item or "\"" in request_item else request_item
                matched_item = f'"{matched_item.replace("\"", "\"\"")}"' if "," in matched_item or "\"" in matched_item else matched_item
                
                # Add row to CSV
                csv_content += f"{request_item},{matched_item},{quantity},{unit_price},{total}\n"
            
            # Return CSV as file download
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=sales_order_{sales_order_id}.csv",
                    "Content-Type": "text/csv",
                    # Add Cache-Control header to prevent caching
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Failed to generate CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV: {str(e)}") 