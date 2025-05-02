from fastapi import HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from io import StringIO
import logging

from app.models.sales_order import SalesOrderModel, LineItem
from app.services.matching_service import match_batch_items

logger = logging.getLogger(__name__)

async def create_sales_order(db, session, file_name: str, line_items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a new sales order in the database
    """
    try:
        logger.info(f"Creating sales order with file_name: {file_name}")
        # Convert the extracted data to LineItem objects
        line_items = []
        for item in line_items_data:
            # Process the item to ensure it has the correct fields
            processed_item = {}
            
            # Ensure the Request Item field is present
            if "Request Item" in item:
                processed_item["Request Item"] = item["Request Item"]
            else:
                # Skip items without Request Item
                logger.warning(f"Skipping item without Request Item: {item}")
                continue
            
            # Handle Amount/Quantity field
            if "Quantity" in item:
                processed_item["Quantity"] = item["Quantity"]
            if "Amount" in item:
                processed_item["Amount"] = item["Amount"]
            
            # Handle Unit Price field
            if "Unit Price" in item:
                processed_item["Unit Price"] = item["Unit Price"]
            
            # Handle Total field
            if "Total" in item:
                processed_item["Total"] = item["Total"]
            
            # Handle match fields
            if "matched_item" in item:
                processed_item["matched_item"] = item["matched_item"]
            if "match_score" in item:
                processed_item["match_score"] = item["match_score"]
            
            # Add to line items
            line_items.append(LineItem(**processed_item))
        
        # Create the sales order
        sales_order = SalesOrderModel(
            file_name=file_name,
            line_items=line_items
        )
        
        # Insert the sales order into the database - no transaction
        result = await db.sales_orders.insert_one(sales_order.dict(by_alias=True))
        
        # Return the created sales order with ID
        created_sales_order = await db.sales_orders.find_one({"_id": result.inserted_id})
        return created_sales_order
        
    except Exception as e:
        logger.exception(f"Error creating sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating sales order: {str(e)}")

async def match_sales_order_items(db, session, sales_order_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Match all line items in a sales order with products
    """
    try:
        logger.info(f"Matching items for sales order: {sales_order_id}")
        
        # Get the sales order
        sales_order = await db.sales_orders.find_one({"_id": sales_order_id})
        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales order not found")
        
        # Extract item names for matching
        item_queries = [item["Request Item"] for item in sales_order["line_items"]]
        
        # Match the items
        match_results = await match_batch_items(item_queries, limit)
        
        # Update the line items with match results
        updated_line_items = []
        for item in sales_order["line_items"]:
            request_item = item["Request Item"]
            matches = match_results.get(request_item, [])
            
            updated_item = item.copy()
            if matches:
                # Use the best match as the default match
                updated_item["matched_item"] = matches[0]["match"]
                updated_item["match_score"] = matches[0]["score"]
                updated_item["alternate_matches"] = matches[1:] if len(matches) > 1 else []
            else:
                updated_item["matched_item"] = None
                updated_item["match_score"] = None
                updated_item["alternate_matches"] = []
                
            updated_line_items.append(updated_item)
        
        # Update the sales order
        await db.sales_orders.update_one(
            {"_id": sales_order_id},
            {
                "$set": {
                    "line_items": updated_line_items,
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Return the updated sales order
        updated_sales_order = await db.sales_orders.find_one({"_id": sales_order_id})
        return updated_sales_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error matching sales order items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error matching sales order items: {str(e)}")

async def update_sales_order(db, session, sales_order_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a sales order with new information
    """
    try:
        logger.info(f"Updating sales order: {sales_order_id}")
        
        # Add updated timestamp
        updates["updated_at"] = datetime.now()
        
        # Update the sales order
        result = await db.sales_orders.update_one(
            {"_id": sales_order_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Sales order not found")
        
        # Return the updated sales order
        updated_sales_order = await db.sales_orders.find_one({"_id": sales_order_id})
        return updated_sales_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating sales order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating sales order: {str(e)}")

async def get_sales_order_csv(db, session, sales_order_id: str) -> str:
    """
    Generate a CSV representation of a sales order
    """
    try:
        logger.info(f"Generating CSV for sales order: {sales_order_id}")
        
        # Get the sales order
        sales_order = await db.sales_orders.find_one({"_id": sales_order_id})
        if not sales_order:
            raise HTTPException(status_code=404, detail="Sales order not found")
        
        # Convert to DataFrame
        items = []
        for item in sales_order["line_items"]:
            item_data = {
                "Request Item": item["Request Item"],
                "Matched Product": item.get("matched_item", ""),
            }
            
            # Add quantity - prefer Quantity over Amount
            if "Quantity" in item:
                item_data["Quantity"] = item["Quantity"]
            elif "Amount" in item:
                item_data["Quantity"] = item["Amount"]
            
            # Add other fields
            item_data["Unit Price"] = item.get("Unit Price")
            item_data["Total"] = item.get("Total")
            
            items.append(item_data)
        
        df = pd.DataFrame(items)
        
        # Convert to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating CSV: {str(e)}") 