# Sales Order Processor - Backend

This is the backend application for the Sales Order Processor, built with FastAPI.

## Features

- PDF extraction using external API
- Product matching using external APIs
- MongoDB database for storage
- CSV export functionality

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with the following variables:
   ```
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=sales_orders_db
   EXTRACTION_API_URL=https://plankton-app-qajlk.ondigitalocean.app/extraction_api
   MATCH_BATCH_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app/match/batch
   MATCH_SINGLE_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app/match
   ```

4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

5. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /api/extract` - Extract data from PDF file
- `POST /api/sales-orders` - Create a new sales order
- `GET /api/sales-orders` - Get all sales orders
- `GET /api/sales-orders/{id}` - Get a specific sales order
- `POST /api/sales-orders/{id}/match` - Match all items in a sales order
- `GET /api/sales-orders/{id}/match-item` - Get matches for a specific item
- `PATCH /api/sales-orders/{id}` - Update a sales order
- `PATCH /api/sales-orders/{id}/line-items/{index}` - Update a specific line item
- `GET /api/sales-orders/{id}/csv` - Download a sales order as CSV 