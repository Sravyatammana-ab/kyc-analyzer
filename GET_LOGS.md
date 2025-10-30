# 📋 How to Get the Right Logs

## What I Saw
The logs you shared show server startup/shutdown only.

## What I Need
I need to see what happens **WHEN YOU UPLOAD THE PASSPORT**.

## Step-by-Step Instructions

### Step 1: Start Clean
Open a NEW terminal and run:
```powershell
cd "D:\Cerevyn Solutions\kyc analyser"
uvicorn main:app --reload
```

Wait for:
```
INFO: Application startup complete.
```

### Step 2: Upload Passport
1. Open Postman
2. POST to `http://localhost:8000/analyze`
3. Upload "manoj passport front.jpg"
4. Click **Send**

### Step 3: Watch Terminal
**You'll see NEW logs appear** like:
```
INFO: Processing file: manoj passport front.jpg
INFO: Extracting text from image using Tesseract OCR...
INFO: Loaded image: mode=RGB, size=(...)
INFO: Attempting simple OCR without preprocessing...
...
```

### Step 4: Copy THE NEW LOGS
Copy everything from the upload request, starting with:
```
INFO: Processing file: ...
```

And ending when you see the response in Postman.

## What These Logs Will Show

✅ If OCR extracted text:
```
INFO: Simple OCR succeeded! Extracted 523 characters
INFO: First 200 chars: REPUBLIC OF INDIA...
```

❌ If OCR failed:
```
INFO: Simple OCR returned empty text
INFO: Trying OCR with light preprocessing...
INFO: All OCR attempts returned empty
```

## Please Try Again

1. Start server
2. Upload passport in Postman
3. Copy the logs that appear AFTER you click Send
4. Share those logs here

**I need the processing logs, not the startup logs!** 📋

