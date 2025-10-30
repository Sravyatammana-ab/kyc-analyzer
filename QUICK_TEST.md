# Quick Test Guide for Postman

## 🚀 Fast Testing (5 Minutes)

### 1. Start Server
```bash
uvicorn main:app --reload
```

### 2. Open Postman
1. Open Postman application

### 3. Import Collection
1. Click **"Import"** button
2. Select file: `Document_Analysis_API.postman_collection.json`
3. Click **"Import"**

### 4. Test
1. Click **"Health Check"** → Click **"Send"** ✅ Should see: `{"status": "ok"}`
2. Click **"Analyze Document"**:
   - Body tab → **form-data**
   - Key: `file` (type: **File**)
   - Click **"Select Files"** → Choose your KYC document
   - Click **"Send"** 🎉

### 5. View Results
Check the response for:
- ✅ Document type (PAN, Aadhar, etc.)
- ✅ AI summary
- ✅ Extracted key details
- ✅ Validation dates (for Passport/Driving Licence)

---

## 📋 What to Test

| Document Type | Expected Fields | Validation Dates |
|--------------|----------------|------------------|
| **PAN** | PAN Number, Name, Father's Name, DOB | ❌ |
| **Aadhar** | Aadhar Number, Name, DOB, Gender, Address | ❌ |
| **Driving Licence** | Licence Number, Name, DOB, Address | ✅ **Valid From/Until** |
| **Passport** | Passport Number, Name, DOB, Nationality | ✅ **Issue/Expiry** |
| **Utility Bill** | Account Number, Name, Address, Bill Date | ❌ |

---

## ⚠️ Quick Troubleshooting

| Error | Solution |
|-------|----------|
| Connection refused | Server not running → `uvicorn main:app --reload` |
| Failed to extract text | Install Tesseract OCR or use digital PDF |
| Empty response | Check OpenAI API key or document quality |

---

## 📁 Sample API Request

**Method:** POST  
**URL:** `http://localhost:8000/analyze`  
**Body:** form-data  
- Key: `file` (File type)  
- Value: [Select document]

**Success Response:**
```json
{
  "filename": "pan_card.pdf",
  "document_type": "PAN",
  "analysis": {
    "language": "English",
    "document_type": "PAN",
    "summary": "This is a PAN card...",
    "extracted_data": {
      "PAN Number": "ABCDE1234F",
      "Name": "John Doe",
      ...
    }
  }
}
```

---

**That's it!** For detailed instructions, see `POSTMAN_TESTING_GUIDE.md`

