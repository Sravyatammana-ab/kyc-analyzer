# How to Fix Tesseract Path Issue on Windows

## Problem
Getting error: `"Failed to extract text from document. Please check if the document is readable and Tesseract OCR is installed."`

## Solution

The code now auto-detects Tesseract, but if it still doesn't work, follow these steps:

### Step 1: Find Your Tesseract Installation Path

**Option A: Check Common Locations**
1. Open File Explorer
2. Check these folders:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
   - Check your Downloads folder if you installed it recently

**Option B: Search for it**
1. Click Start → Type "tesseract.exe"
2. Right-click → "Open file location"
3. Copy the full path

**Option C: Via Command Prompt**
1. Open Command Prompt
2. Type: `where tesseract`
3. Copy the path shown

### Step 2: Create .env File

1. In your project root folder (`d:\Cerevyn Solutions\kyc analyser\`), create a new file called `.env`
2. Add this line (replace with YOUR actual path):
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Example:**
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
OPENAI_API_KEY="open_api_key"
```

### Step 3: Restart Server

1. Stop the running server (Ctrl+C in terminal)
2. Start it again:
```bash
uvicorn main:app --reload
```

### Step 4: Test Again

Try uploading your Aadhar image in Postman again.

---

## Alternative: If Tesseract is NOT Installed

### Install Tesseract OCR on Windows:

1. **Download Installer:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.x.x.exe` (latest version)

2. **Install:**
   - Run the installer
   - **Important:** During installation, check **"Add to PATH"** option
   - Click Next → Install

3. **Verify Installation:**
   - Open Command Prompt
   - Type: `tesseract --version`
   - Should show version number

4. **Find Installation Path:**
   - Usually: `C:\Program Files\Tesseract-OCR\tesseract.exe`

5. **Add to .env file:**
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## Quick Test to Verify Tesseract Works

Open Python and test:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
print(pytesseract.get_tesseract_version())
```

Should print version number (e.g., `5.4.0`).

---

## Troubleshooting

### Error: "TesseractNotFoundError"

**Solution:** Tesseract path is wrong or not installed.

### Error: "Failed to extract text"

**Possible causes:**
1. Image quality is too poor
2. Image is corrupt
3. Tesseract can't read the image format

**Solution:** Try with a clearer, higher quality image.

### Still Getting 500 Error?

1. Check server logs for specific error
2. Verify Tesseract path in .env file
3. Restart server after making changes
4. Try with a different document format (PDF instead of image)

---

## After Fixing

✅ Server starts without errors  
✅ Upload image in Postman  
✅ Get successful response with extracted data  

---

**Your .env file should look like:**
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe


Save the file and restart your server!

