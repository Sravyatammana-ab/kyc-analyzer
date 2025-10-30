# KYC Document Analysis API

A FastAPI-based backend service for analyzing KYC (Know Your Customer) documents using OpenAI GPT and OCR technologies.

## Features

- **Document Type Classification**: Automatically identifies document types (PAN, Aadhar, Driving Licence, Passport, Utility Bills)
- **Key Information Extraction**: Extracts important details from KYC documents
- **Validation Date Extraction**: Automatically extracts validation dates for Passport and Driving Licence
- **OCR Support**: Uses Tesseract OCR for scanned documents and images
- **Multiple Format Support**: PDF, DOCX, CSV, XLSX, PNG, JPG, JPEG

## Document Types Supported

1. **PAN Card**: PAN Number, Name, Father's Name, Date of Birth, Signature
2. **Aadhar Card**: Aadhar Number, Name, Date of Birth, Gender, Address
3. **Driving Licence**: Licence Number, Name, Date of Birth, Valid From, Valid Until, Address, Vehicle Classes
4. **Passport**: Passport Number, Name, Date of Birth, Place of Birth, Issue Date, Expiry Date, Nationality
5. **Utility Bills**: Account Number, Name, Address, Bill Date, Bill Amount, Service Type

## Setup

### Prerequisites

1. Python 3.8+
2. Tesseract OCR installed on your system
   - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional, API key is hardcoded):
   - `OPENAI_API_KEY`: Your OpenAI API key (default is hardcoded in openai_service.py)
   - `TESSERACT_CMD`: Path to Tesseract executable (if not in system PATH)

3. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### GET `/`
Returns API information and available endpoints.

### GET `/health`
Health check endpoint.

### POST `/analyze`
Upload and analyze a KYC document.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (pdf, docx, csv, xlsx, png, jpg, jpeg)

**Response:**
```json
{
  "filename": "document.pdf",
  "document_type": "PAN",
  "analysis": {
    "language": "English",
    "document_type": "PAN",
    "summary": "This is a PAN card issued to John Doe...",
    "extracted_data": {
      "PAN Number": "ABCDE1234F",
      "Name": "John Doe",
      "Father's Name": "Robert Doe",
      "Date of Birth": "1990-01-15",
      "Signature": "John Doe"
    }
  }
}
```

## Response Format

The API returns structured JSON with:
- **language**: Detected language of the document
- **document_type**: Type of KYC document
- **summary**: Brief AI-generated summary
- **extracted_data**: Key-value pairs of extracted information

For Passport and Driving Licence, the response includes validation dates:
- **Valid From**: Start date
- **Valid Until/Expiry Date**: End date

## Technologies Used

- **FastAPI**: Web framework
- **OpenAI GPT-4**: Document analysis and classification
- **Tesseract OCR**: Text extraction from images and scanned documents
- **PDF Plumber**: PDF text extraction
- **Python-docx**: Word document processing
- **Pandas**: Excel/CSV processing
- **Pillow**: Image processing

## Error Handling

The API handles various error scenarios:
- Unsupported file types
- Failed text extraction
- Invalid document formats
- API errors

All errors return appropriate HTTP status codes with descriptive messages.

## CORS Configuration

Currently configured to allow all origins. **Update this for production use** in `main.py`:

```python
allow_origins=["https://yourfrontend.com"]
```

## Security Note

⚠️ **Important**: The API key is currently hardcoded in the service file. For production, use environment variables or a secure secrets management system.

## License

Copyright (c) 2024 Cerevyn Solutions

