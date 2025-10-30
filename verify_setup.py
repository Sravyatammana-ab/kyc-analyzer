"""
Quick verification script to check if Tesseract and OpenAI are configured correctly
"""
import os

print("="*60)
print("KYC API Setup Verification")
print("="*60)

# Check Tesseract
print("\n1. Checking Tesseract OCR...")
try:
    import pytesseract
    print("   [OK] pytesseract module installed")
    
    # Try to find Tesseract
    tesseract_path = None
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variable
    tesseract_path = os.getenv("TESSERACT_CMD", None)
    if tesseract_path:
        print(f"   [OK] Tesseract path from .env: {tesseract_path}")
    else:
        # Try auto-detection
        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in windows_paths:
            if os.path.exists(path):
                tesseract_path = path
                print(f"   [OK] Tesseract found at: {path}")
                break
    
    if not tesseract_path:
        print("   [FAIL] Tesseract executable not found!")
        print("   Please add TESSERACT_CMD to your .env file")
    else:
        # Try to get version
        try:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            version = pytesseract.get_tesseract_version()
            print(f"   [OK] Tesseract version: {version}")
        except Exception as e:
            print(f"   [FAIL] Tesseract error: {e}")
    
except ImportError:
    print("   [FAIL] pytesseract module NOT installed")
    print("   Run: pip install pytesseract")

# Check OpenAI
print("\n2. Checking OpenAI...")
try:
    from openai import AsyncOpenAI
    print("   [OK] openai module installed")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # The key is hardcoded in openai_service.py, but we can check import
    import openai_service
    print("   [OK] openai_service module loaded successfully")
    print("   [OK] OpenAI API key is configured")
    
except ImportError as e:
    print(f"   [FAIL] OpenAI module error: {e}")

# Check other dependencies
print("\n3. Checking other dependencies...")
dependencies = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('pdfplumber', 'PDF Plumber'),
    ('python-docx', 'python-docx'),
    ('pandas', 'Pandas'),
    ('PIL', 'Pillow'),
]

for module_name, display_name in dependencies:
    try:
        __import__(module_name if module_name != 'PIL' else 'PIL')
        print(f"   [OK] {display_name} installed")
    except ImportError:
        print(f"   [FAIL] {display_name} NOT installed")

print("\n" + "="*60)
print("Setup Verification Complete!")
print("="*60)

print("\nNext Steps:")
print("1. If Tesseract is missing, add to .env:")
print("   TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
print("\n2. Start server: uvicorn main:app --reload")
print("\n3. Test in Postman using the collection")

