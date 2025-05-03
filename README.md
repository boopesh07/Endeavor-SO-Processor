# Endeavor Sales Order Processor

A web application for extracting, normalizing, and processing sales orders from PDF documents.

## Video Walkthrough

[Watch the video walkthrough](https://drive.google.com/file/d/1ijDM_huSl2nSlIeEDqxvoKVcmhRUMLrq/view?usp=sharing)

## Features

- PDF data extraction with intelligent field detection
- Field normalization using OpenAI (Unit Cost → Unit Price, Qty → Quantity)
- MongoDB storage for processed sales orders
- CSV export functionality
- Automatic calculation of missing values
- Fallback manual normalization when AI processing fails

## Tech Stack

### Backend
- FastAPI
- MongoDB
- PyMongo
- Motor (Async MongoDB driver)
- OpenAI API
- PDF extraction tools

### Frontend
- React
- Material UI
- Axios

## Prerequisites

- Python 3.10+ 
- Node.js 14+ 
- MongoDB 4.4+ (standalone server)
- OpenAI API key (for field normalization)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/endeavor-so-processor.git
cd endeavor-so-processor
```

### 2. Set up the backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and update with your values
cp ../.env.example .env
```

### 3. Set up the frontend

```bash
cd ../frontend

# Install dependencies
npm install
```

## Configuration

1. Make sure MongoDB is running on your local machine or update the connection string in your `.env` file
2. Set up your OpenAI API key in the `.env` file for LLM field normalization

## Running the Application

### Start the backend server

```bash
cd backend
source venv/bin/activate  # If not already activated
uvicorn app.main:app --reload
```

The backend API will be available at http://localhost:8000

### Start the frontend development server

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

## Usage

1. Access the web application at http://localhost:3000
2. Upload a sales order PDF
3. The application will extract line items from the PDF
4. Field names will be normalized (Unit Cost → Unit Price, Qty → Quantity)
5. View the extracted data and make any necessary edits
6. Save the sales order
7. Download the data as CSV if needed

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/extract` - Extract data from PDF
- `POST /api/sales-orders` - Create new sales order
- `GET /api/sales-orders` - Get all sales orders
- `GET /api/sales-orders/{id}` - Get specific sales order
- `GET /api/sales-orders/{id}/csv` - Download sales order as CSV

## Troubleshooting

### MongoDB Connection Issues

Make sure MongoDB is running with:

```bash
mongod --version
```

If you're using a different MongoDB connection string, update it in your `.env` file.

### PDF Extraction Problems

If PDF extraction fails:
- Check that the PDF is not password protected
- Ensure the PDF is not a scanned image (OCR might be required)
- Check the PDF format is standard and readable

### OpenAI API Issues

If field normalization fails:
- Verify your OpenAI API key is correct
- Check your API usage and limits
- The application will fall back to manual normalization if AI fails


