"""
Test OCR directly on an image file to debug what's happening
"""
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Passport OCR Direct Test")
print("="*60)

# Test 1: Check if pytesseract works
print("\n1. Testing pytesseract import...")
try:
    import pytesseract
    from PIL import Image
    print("   [OK] Import successful")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Configure Tesseract
print("\n2. Configuring Tesseract...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    tesseract_path = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        tessdata_dir = os.path.join(os.path.dirname(tesseract_path), 'tessdata')
        if os.path.exists(tessdata_dir):
            os.environ['TESSDATA_PREFIX'] = tessdata_dir
        print(f"   [OK] Tesseract configured: {tesseract_path}")
    else:
        print(f"   [FAIL] Tesseract not found at: {tesseract_path}")
        sys.exit(1)
except Exception as e:
    print(f"   [FAIL] Configuration failed: {e}")
    sys.exit(1)

# Test 3: Try to get Tesseract version
print("\n3. Testing Tesseract connection...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"   [OK] Tesseract version: {version}")
except Exception as e:
    print(f"   [FAIL] Failed to get version: {e}")
    sys.exit(1)

# Test 4: Test with actual image
print("\n4. Testing OCR with actual image...")
print("   Looking for: manoj passport front.jpg")

image_path = "manoj passport front.jpg"
if not os.path.exists(image_path):
    # Try to find any jpg file
    jpg_files = list(Path('.').glob('*.jpg'))
    if jpg_files:
        image_path = str(jpg_files[0])
        print(f"   Found: {image_path}")
    else:
        print("   [FAIL] No image file found!")
        print("   Please place 'manoj passport front.jpg' in the project folder")
        sys.exit(1)

try:
    # Load image
    image = Image.open(image_path)
    print(f"   [OK] Image loaded: {image.mode}, size: {image.size}")
    
    # Try OCR without any preprocessing
    print("\n   Attempting OCR without preprocessing...")
    text = pytesseract.image_to_string(image, lang='eng')
    
    if text.strip():
        print(f"   [OK] OCR succeeded!")
        print(f"   Extracted {len(text)} characters")
        print("\n   First 500 characters:")
        print("   " + "-"*56)
        print("   " + text[:500].replace('\n', '\n   '))
        print("   " + "-"*56)
    else:
        print("   [FAIL] OCR returned empty text")
        
        # Try with different configs
        print("\n   Trying with PSM 6 config...")
        text = pytesseract.image_to_string(image, lang='eng', config='--oem 3 --psm 6')
        if text.strip():
            print(f"   [OK] OCR with PSM 6 succeeded!")
            print(f"   Extracted {len(text)} characters")
            print(f"   First 200 chars: {text[:200]}")
        else:
            print("   [FAIL] PSM 6 also returned empty")
            
            # Try with PSM 3
            print("\n   Trying with PSM 3 config...")
            text = pytesseract.image_to_string(image, lang='eng', config='--oem 3 --psm 3')
            if text.strip():
                print(f"   [OK] OCR with PSM 3 succeeded!")
                print(f"   Extracted {len(text)} characters")
                print(f"   First 200 chars: {text[:200]}")
            else:
                print("   [FAIL] PSM 3 also returned empty")
                print("\n   ERROR: All OCR attempts failed!")
                print("   This suggests the image quality or content may not be suitable for OCR")
                
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test Complete!")
print("="*60)

