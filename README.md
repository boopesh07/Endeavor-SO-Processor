# Sales Order Processor

An automated document processing application for sales order entry. This application extracts data from sales order PDFs, matches items with a product catalog, and stores the processed orders in MongoDB.

## Video Explanation
[Watch a detailed walkthrough of the application](https://drive.google.com/file/d/1ijDM_huSl2nSlIeEDqxvoKVcmhRUMLrq/view?usp=sharing)

## Project Structure

- **backend/**: FastAPI backend application
- **frontend/**: React frontend application

## Features

- Upload PDF sales orders
- Extract line items using an external API
- Allow editing of extracted data
- Match items with product catalog using external matching APIs
- Store processed orders in MongoDB
- Download processed orders as CSV

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB running locally or accessible via connection string

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=sales_orders_db
   EXTRACTION_API_URL=https://plankton-app-qajlk.ondigitalocean.app/extraction_api
   MATCH_BATCH_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app/match/batch
   MATCH_SINGLE_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app/match
   ```

5. Run the backend:
   ```
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Application Flow

1. **Upload PDF**: User uploads a sales order PDF
2. **Extract Data**: System extracts line items from the PDF
3. **Review/Edit**: User reviews and can edit the extracted data
4. **Save**: Data is saved to MongoDB
5. **Match**: Items are matched with the product catalog
6. **Adjust Matches**: User can adjust the matched products if needed
7. **Download**: User can download the processed order as CSV

## Technologies Used

### Backend
- FastAPI
- MongoDB with Motor (async driver)
- Python httpx for API requests
- Pandas for CSV generation
- OpenAI API for field normalization

### Frontend
- React
- React Router for navigation
- React Bootstrap for UI
- Axios for API communication
- React Dropzone for file uploads


