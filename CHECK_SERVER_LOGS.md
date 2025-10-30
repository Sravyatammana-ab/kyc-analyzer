# 🔍 How to Check Server Logs

## Step-by-Step Instructions

### 1. Start the Server
Open a terminal in your project folder and run:
```bash
uvicorn main:app --reload
```

### 2. Upload Passport in Postman
- Open Postman
- POST to `http://localhost:8000/analyze`
- Upload your passport image

### 3. Watch the Terminal

**Look for these log messages:**

#### ✅ **Success Case:**
```
INFO: Loaded image: mode=RGB, size=(1200, 800)
INFO: Attempting simple OCR without preprocessing...
INFO: Simple OCR succeeded! Extracted 523 characters
INFO: First 200 chars: REPUBLIC OF INDIA P W9699466...
INFO: Successfully extracted text from image using Tesseract OCR
```

#### ❌ **Failure Case:**
```
INFO: Loaded image: mode=RGB, size=(1200, 800)
INFO: Attempting simple OCR without preprocessing...
INFO: Simple OCR returned empty text
INFO: Trying OCR with light preprocessing...
INFO: Light preprocessing OCR still returned empty
INFO: Trying alternative OCR configurations...
INFO: All OCR attempts returned empty or failed
```

### 4. Copy the Logs
**Copy and paste the terminal logs here** so I can see exactly what's happening.

## What I Need to See

Please copy:
1. **Image loading info** - size, mode
2. **OCR attempt results** - whether it extracted text
3. **Any error messages**
4. **Final result** - text length extracted

## Expected Logs for Working OCR

```
INFO: extract_text_from_upload called: file_path=manoj passport front.jpg, file_size=245KB
INFO: Tesseract available: True, Path: C:\Program Files\Tesseract-OCR\tesseract.exe
INFO: Extract text from image using Tesseract OCR...
INFO: Loaded image: mode=RGB, size=(1200, 800)
INFO: Attempting simple OCR without preprocessing...
INFO: Simple OCR succeeded! Extracted 523 characters
INFO: First 200 chars: REPUBLIC OF INDIA P W9699466...
INFO: Successfully extracted text from image using Tesseract OCR. Text length: 523
INFO: Classifying KYC document type with OpenAI...
INFO: Analyzing KYC document with OpenAI. Type: Passport
```

## Next Steps

Once you share the logs, I can:
- See if OCR is working
- See if preprocessing is breaking the image
- See if there are configuration issues
- Fix the exact problem

**Please restart server, upload passport, and share the terminal logs!** 📋

