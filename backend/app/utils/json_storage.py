import json
import os
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Define the storage directory
STORAGE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "data"

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def ensure_storage_dir():
    """Ensure the storage directory exists"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    sales_orders_file = STORAGE_DIR / "sales_orders.json"
    if not sales_orders_file.exists():
        with open(sales_orders_file, "w") as f:
            json.dump([], f)

def get_sales_orders() -> List[Dict[str, Any]]:
    """Get all sales orders from the JSON file"""
    ensure_storage_dir()
    try:
        with open(STORAGE_DIR / "sales_orders.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("Sales orders file not found or invalid, creating new one")
        return []

def save_sales_orders(sales_orders: List[Dict[str, Any]]):
    """Save sales orders to the JSON file"""
    ensure_storage_dir()
    with open(STORAGE_DIR / "sales_orders.json", "w") as f:
        json.dump(sales_orders, f, indent=2, cls=DateTimeEncoder)

def create_sales_order(file_name: str, line_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a new sales order and save it to the JSON file"""
    sales_orders = get_sales_orders()
    
    # Create a new sales order
    new_order = {
        "_id": str(uuid.uuid4()),
        "file_name": file_name,
        "line_items": line_items,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "pending"
    }
    
    # Add the new order to the list
    sales_orders.append(new_order)
    
    # Save the updated list
    save_sales_orders(sales_orders)
    
    return new_order

def get_sales_order_by_id(sales_order_id: str) -> Optional[Dict[str, Any]]:
    """Get a sales order by ID"""
    sales_orders = get_sales_orders()
    for order in sales_orders:
        if order["_id"] == sales_order_id:
            return order
    return None

def update_sales_order(sales_order_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a sales order"""
    sales_orders = get_sales_orders()
    
    # Find the order to update
    updated_order = None
    for i, order in enumerate(sales_orders):
        if order["_id"] == sales_order_id:
            # Update the fields
            for key, value in updates.items():
                order[key] = value
            
            # Update the timestamp
            order["updated_at"] = datetime.now()
            updated_order = order
            break
    
    if updated_order is None:
        raise ValueError(f"Sales order with ID {sales_order_id} not found")
    
    # Save the updated list
    save_sales_orders(sales_orders)
    
    return updated_order

def update_line_item(sales_order_id: str, item_index: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update a specific line item in a sales order"""
    sales_orders = get_sales_orders()
    
    # Find the order to update
    updated_order = None
    for i, order in enumerate(sales_orders):
        if order["_id"] == sales_order_id:
            # Make sure the item index is valid
            if item_index < 0 or item_index >= len(order["line_items"]):
                raise ValueError(f"Invalid line item index: {item_index}")
            
            # Update the line item
            for key, value in updates.items():
                order["line_items"][item_index][key] = value
            
            # Update the timestamp
            order["updated_at"] = datetime.now()
            updated_order = order
            break
    
    if updated_order is None:
        raise ValueError(f"Sales order with ID {sales_order_id} not found")
    
    # Save the updated list
    save_sales_orders(sales_orders)
    
    return updated_order

def delete_sales_order(sales_order_id: str) -> bool:
    """Delete a sales order"""
    sales_orders = get_sales_orders()
    
    # Find the order to delete
    for i, order in enumerate(sales_orders):
        if order["_id"] == sales_order_id:
            # Remove the order
            sales_orders.pop(i)
            
            # Save the updated list
            save_sales_orders(sales_orders)
            
            return True
    
    return False 