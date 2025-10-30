# 🚀 Quick Start - Testing in Postman

## Your setup is ready! ✅

Everything is configured correctly:
- ✓ Tesseract OCR: Installed and configured
- ✓ OpenAI API: Configured with your API key
- ✓ All dependencies: Installed

---

## 🎯 Quick Testing (3 Steps)

### STEP 1: Start Server
```bash
uvicorn main:app --reload
```

Wait until you see:
```
Application startup complete.
```

### STEP 2: Create Postman Request

1. Open Postman
2. Click **New** → **HTTP Request**
3. Set Method to **POST**
4. URL: `http://localhost:8000/analyze`

### STEP 3: Upload Document

1. Go to **Body** tab
2. Select **form-data**
3. Add new row:
   - **Key:** `file` (make sure type is **File**, not Text)
   - **Value:** Click "Select Files" → Choose your KYC document
4. Click **Send** 🚀

---

## ✅ Expected Result

**Status:** `200 OK` (green)

**Response:**
```json
{
  "filename": "your_document.jpg",
  "document_type": "PAN",
  "analysis": {
    "language": "English",
    "document_type": "PAN",
    "summary": "Brief AI-generated summary...",
    "extracted_data": {
      "PAN Number": "...",
      "Name": "...",
      ...
    }
  }
}
```

---

## 📋 What You Can Test

| Document Type | What Gets Extracted | Validation Dates |
|--------------|---------------------|------------------|
| **PAN** | PAN Number, Name, Father's Name, DOB | ❌ |
| **Aadhar** | Aadhar Number, Name, DOB, Gender, Address | ❌ |
| **Driving Licence** | Licence Number, Name, DOB, Address, Classes | ✅ **Valid From/Until** |
| **Passport** | Passport Number, Name, DOB, Nationality | ✅ **Issue/Expiry** |
| **Utility Bill** | Account Number, Name, Address, Bill Date, Amount | ❌ |

---

## ⚠️ If You Get Errors

### Error: Connection refused
→ Server not running. Run: `uvicorn main:app --reload`

### Error: Failed to extract text
→ Try with a clearer image or digital PDF

### Error: Empty response
→ Check server logs in terminal for details

---

## 📚 Full Documentation

- **Detailed Setup:** See `POSTMAN_MANUAL_SETUP.md`
- **Configuration Help:** See `FIX_TESSERACT_WINDOWS.md`
- **General Info:** See `README.md`

---

## 🎉 You're All Set!

**Just run these 3 commands:**

```bash
# 1. Start server
uvicorn main:app --reload
```

Then in Postman:
- POST to `http://localhost:8000/analyze`
- Upload document
- Get results!

**Good luck! 🚀**

