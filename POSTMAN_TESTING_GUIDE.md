# Testing KYC API in Postman - Step-by-Step Guide

## Prerequisites

1. ✅ API server is running (`uvicorn main:app --reload`)
2. ✅ Postman installed
3. ✅ KYC document files ready (PDF, DOCX, PNG, JPG, etc.)

## Method 1: Import Existing Collection (Easiest)

### Step 1: Start the Server
Open terminal in your project folder and run:
```bash
uvicorn main:app --reload
```
Wait for: `Application startup complete`

### Step 2: Import Collection to Postman
1. Open Postman
2. Click **"Import"** button (top left)
3. Select **"File"** tab
4. Browse and select: `Document_Analysis_API.postman_collection.json`
5. Click **"Import"**

You should now see a collection called "Document Analysis API" with 3 requests:
- Health Check
- Root Endpoint  
- Analyze Document

### Step 3: Test Health Check
1. Click on **"Health Check"** request
2. Click **"Send"** button
3. You should see response:
```json
{
  "status": "ok"
}
```

### Step 4: Test Document Analysis
1. Click on **"Analyze Document"** request
2. In the **Body** tab, under **form-data**:
   - Find the "file" row
   - Click the dropdown next to "Key" → Select **"File"**
   - Click **"Select Files"** button
   - Choose your KYC document (PDF, DOCX, image, etc.)
3. Click **"Send"** button
4. Wait for the response (may take 10-30 seconds)

### Expected Response Format:
```json
{
  "filename": "pan_card.pdf",
  "document_type": "PAN",
  "analysis": {
    "language": "English",
    "document_type": "PAN",
    "summary": "This document is a PAN card...",
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

---

## Method 2: Manual Setup (Step-by-Step)

### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Name it: **"Analyze Document"**

### Step 2: Configure Request
1. **Method**: Select **"POST"** from dropdown
2. **URL**: Type `http://localhost:8000/analyze`

### Step 3: Set Up Body
1. Click **"Body"** tab
2. Select **"form-data"** option
3. Add new row:
   - **Key**: `file` (Important: Make sure type is "File")
   - **Type**: Change dropdown to **"File"** (not "Text")
   - **Value**: Click **"Select Files"** and choose your document

**Visual Guide:**
```
[Key]        [Type]    [Value]
file   →     File  →   [Select Files]
```

### Step 4: Send Request
1. Click **"Send"** button
2. Wait for response

### Step 5: View Results
You should see the JSON response with:
- Document type classification
- AI summary
- Extracted key details

---

## Method 3: Create Collection from Scratch

### Step 1: Create Collection
1. Click **"New"** → **"Collection"**
2. Name: **"KYC Document Analysis API"**

### Step 2: Add Health Check Request
1. Right-click collection → **"Add Request"**
2. Name: **"Health Check"**
3. Method: **GET**
4. URL: `http://localhost:8000/health`
5. Click **"Save"**

### Step 3: Add Analyze Request
1. Right-click collection → **"Add Request"**
2. Name: **"Analyze Document"**
3. Method: **POST**
4. URL: `http://localhost:8000/analyze`
5. Body → form-data:
   - Key: `file` (type: File)
   - Value: [Select your file]
6. Click **"Save"**

---

## Testing Different Document Types

### Test PAN Card
1. Select a PAN card PDF or image
2. Send request
3. Verify extracted data:
   - PAN Number
   - Name
   - Father's Name
   - Date of Birth
   - Signature

### Test Aadhar Card
1. Select an Aadhar card image or PDF
2. Verify extracted data:
   - Aadhar Number
   - Name
   - Date of Birth
   - Gender
   - Address

### Test Driving Licence
1. Select a Driving Licence PDF or image
2. Verify extracted data:
   - **Valid From** date
   - **Valid Until** date
   - Licence Number
   - Name
   - Address
   - Vehicle Classes

### Test Passport
1. Select a Passport PDF or image
2. Verify extracted data:
   - **Issue Date**
   - **Expiry Date**
   - Passport Number
   - Name
   - Nationality
   - Place of Birth

### Test Utility Bill
1. Select a utility bill PDF or image
2. Verify extracted data:
   - Account Number
   - Name
   - Address
   - Bill Date
   - Bill Amount
   - Service Type

---

## Troubleshooting

### Error: "Connection refused"
**Solution:** Make sure server is running on port 8000
```bash
uvicorn main:app --reload
```

### Error: "Failed to extract text"
**Possible causes:**
- Document is heavily scanned/poor quality
- File format not supported
- Tesseract OCR not installed

**Solution:** 
- Try a clearer image
- Install Tesseract OCR
- Use digital PDF instead of scanned

### Error: "Unsupported file type"
**Solution:** Use only supported formats:
- `.pdf`, `.docx`, `.csv`, `.xlsx`, `.png`, `.jpg`, `.jpeg`

### Empty response
**Check:**
1. Server logs for errors
2. OpenAI API key is valid
3. Document has readable text

---

## Quick Test Checklist

- [ ] Server running on localhost:8000
- [ ] Health check returns `{"status": "ok"}`
- [ ] Can upload PDF file
- [ ] Can upload image file
- [ ] Response includes `document_type`
- [ ] Response includes `analysis` with `extracted_data`
- [ ] Driving Licence shows validation dates
- [ ] Passport shows expiry dates

---

## Additional Tips

### Create Environment Variables
1. Click gear icon (top right)
2. Add new environment: **"Local Development"**
3. Add variables:
   - `base_url`: `http://localhost:8000`
4. Use in requests: `{{base_url}}/analyze`

### Save Responses
1. After successful test, click **"Save Response"**
2. Keep examples for reference

### Create Tests
Add test script in Postman to verify structure:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has document_type", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('document_type');
});

pm.test("Response has analysis", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('analysis');
});
```

---

## Sample Test Files

Use these types of documents for testing:
- PAN Card (PDF/Image)
- Aadhar Card (Image)
- Driving Licence (PDF/Image)
- Passport (PDF/Image)
- Electricity Bill (PDF)
- Water Bill (PDF)

**Note:** For best results, use clear, high-quality images or digital PDFs.

---

## Need Help?

- Check server logs in terminal
- Verify Tesseract OCR installation
- Review OpenAI API quota
- Check file size (should be reasonable)
- Ensure internet connection for OpenAI API

---

Happy Testing! 🚀

