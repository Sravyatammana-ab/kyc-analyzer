# Setup Instructions for KYC Document Analysis API

## Quick Start Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

#### Windows:
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it (default location: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your system PATH or set environment variable:
   ```powershell
   $env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS:
```bash
brew install tesseract
```

### 3. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Test the API

#### Using curl:
```bash
curl -X POST "http://localhost:8000/analyze" -F "file=@path/to/your/document.pdf"
```

#### Using Python test script:
```bash
python test_openai_kyc.py
```

#### Using Postman:
Import the `Document_Analysis_API.postman_collection.json` file into Postman and use the collection.

### 5. API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Supported Document Types

1. **PAN Card** - Extracts PAN Number, Name, Father's Name, Date of Birth, Signature
2. **Aadhar Card** - Extracts Aadhar Number, Name, Date of Birth, Gender, Address
3. **Driving Licence** - Extracts Licence Number, Name, Date of Birth, **Valid From**, **Valid Until**, Address, Vehicle Classes
4. **Passport** - Extracts Passport Number, Name, Date of Birth, Place of Birth, **Issue Date**, **Expiry Date**, Nationality
5. **Utility Bills** - Extracts Account Number, Name, Address, Bill Date, Bill Amount, Service Type

## Supported File Formats

- PDF (.pdf)
- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- CSV files (.csv)
- Images (.png, .jpg, .jpeg)

## Troubleshooting

### Issue: "Tesseract not found"

**Solution:**
- Ensure Tesseract is installed
- On Windows, set the environment variable:
  ```powershell
  $env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

### Issue: "Failed to extract text from document"

**Solution:**
- Verify the document is readable
- For scanned documents, ensure good image quality
- Check that the file format is supported

### Issue: "OpenAI API error"

**Solution:**
- Verify the API key is valid (hardcoded in `openai_service.py`)
- Check your OpenAI account for API usage limits
- Ensure you have internet connectivity

### Issue: "PDF extraction failed"

**Solution:**
- Try converting the PDF to an image and upload as PNG/JPEG
- For scanned PDFs, Tesseract OCR will be used automatically

## Environment Variables (Optional)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Note: If not set, the API key is hardcoded in `openai_service.py`.

## Production Deployment

For production deployment:

1. **Update CORS settings** in `main.py`:
   ```python
   allow_origins=["https://yourfrontend.com"]
   ```

2. **Use environment variables** for the API key instead of hardcoding

3. **Use a production ASGI server**:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## Next Steps

1. Test with sample KYC documents
2. Integrate with your frontend application
3. Deploy to your hosting platform
4. Monitor API usage and costs

## Support

For issues or questions, please refer to the main README.md file or contact the development team.

