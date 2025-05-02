import json
import logging
import os
from typing import List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def process_extracted_data(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process extracted data through an LLM to normalize field names and ensure
    we have proper Quantity, Unit Price, and Total values
    """
    try:
        # Create a prompt for the LLM
        prompt = create_field_mapping_prompt(items)
        
        # Call LLM
        response = client.chat.completions.create(
            model="gpt-4",  # Use gpt-4.1 if available in your account
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes and normalizes extracted sales order data. Your task is to identify Quantity, Unit Price, and Total fields and map them to standardized names."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,  # Keep deterministic
            max_tokens=2000
        )
        
        # Parse the response
        response_text = response.choices[0].message.content
        logger.info(f"LLM response: {response_text}")
        
        try:
            # Try to extract JSON from the response
            processed_items = extract_json_from_response(response_text)
            return processed_items
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            # Return original items with best-effort field mapping
            return normalize_fields_manually(items)
            
    except Exception as e:
        logger.error(f"LLM processing error: {str(e)}")
        # If LLM processing fails, fall back to manual mapping
        return normalize_fields_manually(items)

def create_field_mapping_prompt(items: List[Dict[str, Any]]) -> str:
    """Create a prompt for the LLM to map fields"""
    items_json = json.dumps(items, indent=2)
    
    prompt = f"""
I have extracted data from a sales order PDF. The data contains items with various field names.
Here's the extracted data:

{items_json}

Please normalize this data to have consistent field names. I need the following fields for each item:
1. "Request Item" - The name/description of the item
2. "Quantity" - The number of items (may be in fields like "Quantity", "Qty", "Amount", etc.)
3. "Unit Price" - The price per unit (may be in fields like "Unit Price", "Price", "Unit Cost", etc.)
4. "Total" - The total cost for the line item (may be in fields like "Total", "Amount", "Line Total", etc.)

For each item, please:
1. Keep the "Request Item" field as is
2. Map the quantity field to "Quantity"
3. Map the unit price field to "Unit Price"
4. Map the total amount field to "Total"
5. If a field is missing but can be calculated (e.g., Total = Quantity * Unit Price), please calculate it
6. Keep any other fields that might be useful

Return the normalized data as a JSON array of objects with standardized field names. 
The response should be ONLY the JSON array, with no additional text.
"""
    return prompt

def extract_json_from_response(response_text: str) -> List[Dict[str, Any]]:
    """Extract JSON from the LLM response"""
    # Try to find JSON array in the response
    start_idx = response_text.find('[')
    end_idx = response_text.rfind(']') + 1
    
    if start_idx == -1 or end_idx == 0:
        raise ValueError("No JSON array found in response")
    
    json_str = response_text[start_idx:end_idx]
    return json.loads(json_str)

def normalize_fields_manually(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Manually normalize fields as a fallback"""
    normalized_items = []
    
    for item in items:
        normalized_item = {}
        
        # Copy Request Item field
        if "Request Item" in item:
            normalized_item["Request Item"] = item["Request Item"]
        elif "Item Description" in item:
            normalized_item["Request Item"] = item["Item Description"]
        elif "Description" in item:
            normalized_item["Request Item"] = item["Description"]
        
        # Normalize Quantity fields
        if "Quantity" in item:
            normalized_item["Quantity"] = item["Quantity"]
        elif "Qty" in item:
            normalized_item["Quantity"] = item["Qty"]
        
        # Normalize Unit Price fields
        if "Unit Price" in item:
            normalized_item["Unit Price"] = item["Unit Price"]
        elif "Price" in item:
            normalized_item["Unit Price"] = item["Price"]
        elif "Unit Cost" in item:
            normalized_item["Unit Price"] = item["Unit Cost"]
        
        # Normalize Total fields
        if "Total" in item:
            normalized_item["Total"] = item["Total"]
        elif "Amount" in item and "Quantity" in item and isinstance(item["Amount"], (int, float)):
            # If Amount likely represents a total (not a quantity)
            if item["Amount"] > item["Quantity"]:
                normalized_item["Total"] = item["Amount"]
            
        # Calculate missing Total if possible
        if "Total" not in normalized_item and "Quantity" in normalized_item and "Unit Price" in normalized_item:
            try:
                normalized_item["Total"] = float(normalized_item["Quantity"]) * float(normalized_item["Unit Price"])
            except (TypeError, ValueError):
                pass
        
        # Calculate missing Unit Price if possible
        if "Unit Price" not in normalized_item and "Quantity" in normalized_item and "Total" in normalized_item:
            try:
                if float(normalized_item["Quantity"]) > 0:
                    normalized_item["Unit Price"] = float(normalized_item["Total"]) / float(normalized_item["Quantity"])
            except (TypeError, ValueError, ZeroDivisionError):
                pass
                
        # Preserve other fields that might be useful
        for key, value in item.items():
            if key not in normalized_item and key not in ["Quantity", "Unit Price", "Total", "Request Item"]:
                normalized_item[key] = value
        
        normalized_items.append(normalized_item)
    
    return normalized_items 