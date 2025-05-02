import httpx
from fastapi import HTTPException
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

MATCH_BATCH_API_URL = os.getenv("MATCH_BATCH_API_URL", "https://endeavor-interview-api-gzwki.ondigitalocean.app/match/batch")
MATCH_SINGLE_API_URL = os.getenv("MATCH_SINGLE_API_URL", "https://endeavor-interview-api-gzwki.ondigitalocean.app/match")

async def match_batch_items(queries: List[str], limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """
    Match multiple line items to products using the batch matching API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MATCH_BATCH_API_URL}?limit={limit}",
                json={"queries": queries}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, 
                                    detail=f"Matching API error: {response.text}")
            
            result = response.json()
            return result.get("results", {})
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with matching API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching error: {str(e)}")

async def match_single_item(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Match a single line item to products using the single matching API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MATCH_SINGLE_API_URL}?query=\"{query}\"&limit={limit}"
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, 
                                    detail=f"Matching API error: {response.text}")
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with matching API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching error: {str(e)}") 