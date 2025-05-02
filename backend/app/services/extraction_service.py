import httpx
from fastapi import UploadFile, HTTPException
import os
import logging
from dotenv import load_dotenv
from app.utils.llm_utils import process_extracted_data

load_dotenv()
logger = logging.getLogger(__name__)

EXTRACTION_API_URL = os.getenv("EXTRACTION_API_URL", "https://plankton-app-qajlk.ondigitalocean.app/extraction_api")

async def extract_from_pdf(file: UploadFile):
    """
    Extract line items from a PDF sales order using the extraction API
    and process through LLM to normalize field names
    """
    try:
        # Creating a temporary file for httpx to read from
        file_content = await file.read()
        
        # Reset file pointer for later use if needed
        await file.seek(0)
        
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, file_content, file.content_type)}
            response = await client.post(EXTRACTION_API_URL, files=files)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, 
                                   detail=f"Extraction API error: {response.text}")
            
            # Get the raw extracted data
            raw_data = response.json()
            logger.info(f"Raw extraction data: {raw_data}")
            
            # Process through LLM to normalize field names
            normalized_data = await process_extracted_data(raw_data)
            logger.info(f"Normalized extraction data: {normalized_data}")
            
            return normalized_data
            
    except httpx.RequestError as e:
        logger.error(f"Error communicating with extraction API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with extraction API: {str(e)}")
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}") 