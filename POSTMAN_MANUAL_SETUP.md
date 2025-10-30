# Manual Postman Setup Guide - Step by Step

## ✅ Prerequisites Complete!
- Tesseract OCR installed and configured ✓
- OpenAI API key configured ✓
- All dependencies installed ✓

---

## Step-by-Step Postman Setup

### STEP 1: Start the Server

1. Open your terminal/command prompt in the project folder
2. Run this command:
```bash
uvicorn main:app --reload
```

3. **Wait for this message:**
```
Application startup complete.
```

4. **Keep this terminal window open** (don't close it)

---

### STEP 2: Create New Request in Postman

1. **Open Postman application**

2. Click the **"New"** button (or press `Ctrl + N`)

3. Select **"HTTP Request"**

4. You'll see a blank request template

---

### STEP 3: Configure Request Settings

#### 3a. Set Request Method and URL

1. **Method:** Click the dropdown on the left → Select **"POST"**

2. **URL:** Type this exactly:
```
http://localhost:8000/analyze
```

**Your screen should look like:**
```
[POST ▼]  http://localhost:8000/analyze
```

---

### STEP 4: Configure Body (File Upload)

1. Click the **"Body"** tab (below the URL bar)

2. Select **"form-data"** radio button (on the left side)

3. **Add a new row:**

   **In the KEY column:**
   - Type: `file`
   - Click the dropdown next to it → Change from **"Text"** to **"File"**
   
   **In the VALUE column:**
   - Click **"Select Files"**
   - Browse and select your KYC document (PDF, JPG, PNG, etc.)
   - Click **"Open"**

**Your screen should look like:**
```
[ ✓ Body]
  [● form-data]

  Key       |  Type  |  Value
  ----------|--------|------------------
  file      |  File  |  [durga aadhar front.jpg ▼]
```

---

### STEP 5: Send the Request

1. Click the blue **"Send"** button (top right)

2. **Wait for response** (may take 10-30 seconds)

3. You should see the response in the bottom panel

---

## Expected Success Response

You should see something like this:

```json
{
  "filename": "durga aadhar front.jpg",
  "document_type": "Aadhar",
  "analysis": {
    "language": "English",
    "document_type": "Aadhar",
    "summary": "This is an Aadhar card document...",
    "extracted_data": {
      "Aadhar Number": "1234 5678 9012",
      "Name": "DURGA",
      "Date of Birth": "01-01-1990",
      "Gender": "Female",
      "Address": "..."
    }
  }
}
```

**Status Code:** `200 OK` (in green)

---

## Testing Different Documents

### Test PAN Card
1. Select a PAN card image or PDF
2. Click Send
3. Expected: PAN Number, Name, Father's Name, DOB extracted

### Test Driving Licence
1. Select a driving licence image or PDF
2. Click Send
3. Expected: **Valid From** and **Valid Until** dates included

### Test Passport
1. Select a passport image or PDF
2. Click Send
3. Expected: **Issue Date** and **Expiry Date** included

### Test Aadhar Card
1. Select an Aadhar card image
2. Click Send
3. Expected: Aadhar Number, Name, DOB, Address extracted

### Test Utility Bill
1. Select a utility bill PDF or image
2. Click Send
3. Expected: Account Number, Name, Address, Bill Date extracted

---

## Create Additional Test Requests

### Create Health Check Request

1. Click **"New"** → **"HTTP Request"**
2. Method: **GET**
3. URL: `http://localhost:8000/health`
4. Click **"Send"**
5. Should see: `{"status": "ok"}`

---

## Save Your Requests

### Save Individual Request:
1. After successful test, click **"Save"** button
2. Enter name: "Analyze KYC Document"
3. Click **"Save"**

### Create Collection:
1. Click **"New"** → **"Collection"**
2. Name: "KYC API Tests"
3. Click **"Create"**
4. Drag your saved requests into this collection

---

## Common Issues & Solutions

### Issue 1: "Connection refused"
**Solution:**
- Make sure server is running (`uvicorn main:app --reload`)
- Check if port 8000 is being used by another app
- Try restarting the server

### Issue 2: "Failed to extract text"
**Possible causes:**
- Image quality too poor
- Document is corrupted
- Tesseract not configured properly

**Solution:**
- Try with a clearer, higher quality image
- Use digital PDF instead of scanned image
- Check server logs for specific error

### Issue 3: Empty or Error Response
**Solution:**
- Check terminal logs for error details
- Verify OpenAI API key is working
- Try with a different document

### Issue 4: "File not selected"
**Solution:**
- Make sure you clicked "Select Files" button
- Ensure file type is File (not Text) in form-data
- Try selecting the file again

---

## Quick Test Checklist

- [ ] Server is running (`uvicorn main:app --reload`)
- [ ] Saw "Application startup complete" message
- [ ] Created POST request to `http://localhost:8000/analyze`
- [ ] Set Body to "form-data"
- [ ] Key is "file" with type "File"
- [ ] Selected a KYC document
- [ ] Clicked "Send" button
- [ ] Got 200 OK response with extracted data

---

## Visual Guide for Body Tab

```
┌─────────────────────────────────────────┐
│ Body  [●] form-data  [ ] x-www...  [ ]  │
│                                          │
│  Key     │ Type  │ Value                │
│  ────────┼───────┼───────────────────── │
│  file    │ File ▼│ [Select Files]       │
│  ✓       │       │                      │
└─────────────────────────────────────────┘
```

Make sure:
- ✓ Type is set to **"File"** (not Text)
- ✓ Value shows **[Select Files]** button
- ✓ File is actually selected and shown

---

## Server Logs

While testing, watch your terminal for logs like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Processing file: pan_card.pdf, content_type: application/pdf
INFO:     Successfully extracted text using pdfplumber.
INFO:     Classifying KYC document type with OpenAI...
INFO:     Analyzing KYC document with OpenAI. Type: PAN
INFO:     127.0.0.1:53234 - "POST /analyze HTTP/1.1" 200 OK
```

If you see errors in the logs, that will help diagnose the issue.

---

## Tips for Best Results

1. **Image Quality:** Use high-resolution, clear images
2. **File Size:** Keep files under 10MB for faster processing
3. **Supported Formats:** PDF, DOCX, CSV, XLSX, PNG, JPG, JPEG
4. **Digital Documents:** Work better than scanned images
5. **Orientation:** Ensure documents are right-side up

---

## Next Steps After Testing

Once you verify everything works:

1. **Integrate with Frontend:**
   - Use the same POST endpoint
   - Send file via FormData
   - Handle the JSON response

2. **Production Deployment:**
   - Update CORS settings
   - Use environment variables for API key
   - Deploy to cloud hosting

3. **Add Error Handling:**
   - Handle network errors
   - Show user-friendly messages
   - Implement retry logic

---

**Ready to Test!**

1. Start server: `uvicorn main:app --reload`
2. Open Postman
3. Create POST request to `http://localhost:8000/analyze`
4. Select document file
5. Click Send
6. View results! 🎉

Good luck! 🚀

