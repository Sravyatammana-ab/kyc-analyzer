"""
Direct test of Tesseract OCR to diagnose issues
"""
import sys
from PIL import Image
from io import BytesIO

print("Testing Tesseract OCR directly...")
print("="*60)

# Test 1: Import pytesseract
print("\n1. Testing pytesseract import...")
try:
    import pytesseract
    print("   [OK] pytesseract imported successfully")
except ImportError as e:
    print(f"   [FAIL] Could not import pytesseract: {e}")
    sys.exit(1)

# Test 2: Configure Tesseract path
print("\n2. Configuring Tesseract path...")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Try from .env first
    tesseract_path = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"   [OK] Tesseract path configured: {tesseract_path}")
        
        # Set TESSDATA_PREFIX
        tessdata_dir = os.path.join(os.path.dirname(tesseract_path), 'tessdata')
        if os.path.exists(tessdata_dir):
            os.environ['TESSDATA_PREFIX'] = tessdata_dir
            print(f"   [OK] TESSDATA_PREFIX set to: {tessdata_dir}")
        else:
            print(f"   [WARNING] Tessdata directory not found at: {tessdata_dir}")
    else:
        print(f"   [FAIL] Tesseract not found at: {tesseract_path}")
        sys.exit(1)
except Exception as e:
    print(f"   [FAIL] Error configuring Tesseract: {e}")
    sys.exit(1)

# Test 3: Get Tesseract version
print("\n3. Getting Tesseract version...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"   [OK] Tesseract version: {version}")
except Exception as e:
    print(f"   [FAIL] Could not get version: {e}")
    sys.exit(1)

# Test 4: List available languages
print("\n4. Checking available languages...")
try:
    langs = pytesseract.get_languages()
    print(f"   [OK] Available languages: {', '.join(langs[:5])}...")
    if 'eng' not in langs:
        print("   [WARNING] English language pack not found!")
except Exception as e:
    print(f"   [WARNING] Could not list languages: {e}")

# Test 5: Try OCR on a simple test image (if PIL works)
print("\n5. Testing OCR with a sample image...")
try:
    # Create a simple test image
    test_image = Image.new('RGB', (200, 50), color='white')
    print("   [OK] Created test image")
    
    # Try to extract text (will be empty, but tests if OCR works)
    try:
        text = pytesseract.image_to_string(test_image)
        print(f"   [OK] OCR ran successfully (got {len(text)} characters)")
    except Exception as e:
        print(f"   [FAIL] OCR failed: {e}")
        import traceback
        print(traceback.format_exc())
except Exception as e:
    print(f"   [WARNING] Could not create test image: {e}")

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
print("\nIf all tests passed, Tesseract is configured correctly.")
print("If you're still getting errors, check the server logs when you upload a file.")

