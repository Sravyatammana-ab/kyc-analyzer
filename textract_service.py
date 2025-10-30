from dotenv import load_dotenv
load_dotenv()

import os
import logging
import traceback
import pdfplumber
import pandas as pd
from docx import Document
from PIL import Image
from io import BytesIO
from mimetypes import guess_type

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not installed. OCR functionality will be limited.")

load_dotenv()

# Configure Tesseract path (update this if Tesseract is installed in a different location)
# For Windows, common path: r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# For Linux/Mac: pytesseract will use system PATH
if TESSERACT_AVAILABLE:
    # Prefer env var, then PATH (Linux/Docker), then Windows fallbacks
    TESSERACT_CMD = os.getenv("TESSERACT_CMD")
    if TESSERACT_CMD and os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        logging.info(f"Using Tesseract from TESSERACT_CMD: {TESSERACT_CMD}")
    else:
        try:
            import shutil as _sh
            detected = _sh.which("tesseract")
        except Exception:
            detected = None
        if detected:
            pytesseract.pytesseract.tesseract_cmd = detected
            logging.info(f"Auto-detected Tesseract on PATH: {detected}")
        else:
            windows_paths = [
                r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
                r"C:\\Users\\Public\\Tesseract-OCR\\tesseract.exe"
            ]
            for path in windows_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logging.info(f"Auto-detected Windows Tesseract at: {path}")
                    break

    # Attempt to set TESSDATA_PREFIX for common Linux/Docker paths
    if 'TESSDATA_PREFIX' not in os.environ:
        for candidate in [
            '/usr/share/tesseract-ocr/4.00/tessdata',
            '/usr/share/tesseract-ocr/tessdata'
        ]:
            if os.path.exists(candidate):
                os.environ['TESSDATA_PREFIX'] = candidate
                logging.info(f"Set TESSDATA_PREFIX to: {candidate}")
                break


async def extract_text_from_upload(file_path: str, file_bytes: bytes, mime_type_hint: str = None) -> str:
    """Extracts text from various formats. Uses Tesseract OCR for images and scanned documents."""

    ext = file_path.lower()
    logging.info(f"extract_text_from_upload called: file_path={file_path}, mime_type={mime_type_hint}, file_size={len(file_bytes)} bytes")
    
    # Log Tesseract status
    if TESSERACT_AVAILABLE:
        logging.info(f"Tesseract available: True, Path: {getattr(pytesseract.pytesseract, 'tesseract_cmd', 'Not configured')}")
    else:
        logging.warning("Tesseract NOT available - pytesseract not installed")

    # 1. Extract text from digital PDFs
    if ext.endswith(".pdf"):
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                full_text = "".join(page.extract_text() or "" for page in pdf.pages)
            if full_text.strip():
                logging.info("Successfully extracted text using pdfplumber.")
                return full_text.strip()
        except Exception as e:
            logging.warning(f"pdfplumber failed: {e}. Falling back to Tesseract OCR.")
        
        # Fallback to Tesseract for scanned PDFs
        if TESSERACT_AVAILABLE:
            try:
                logging.info("Attempting Tesseract OCR on PDF pages...")
                with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                    extracted_text = []
                    for page_num, page in enumerate(pdf.pages[:5]):  # Limit to first 5 pages
                        try:
                            image = page.to_image(resolution=200)
                            text = pytesseract.image_to_string(image.original)
                            if text.strip():
                                extracted_text.append(text.strip())
                        except Exception as e:
                            logging.warning(f"OCR failed on page {page_num}: {e}")
                    result = "\n".join(extracted_text)
                    if result.strip():
                        logging.info("Successfully extracted text using Tesseract OCR on PDF.")
                        return result.strip()
            except Exception as e:
                logging.error(f"Tesseract OCR on PDF failed: {e}")
        else:
            logging.warning("Tesseract not available. Cannot perform OCR on scanned PDF.")

    # 2. Extract text from Word documents (.docx)
    elif ext.endswith(".docx"):
        try:
            doc = Document(BytesIO(file_bytes))
            full_text = "\n".join([para.text for para in doc.paragraphs])
            if full_text.strip():
                logging.info("Successfully extracted text from DOCX.")
                return full_text.strip()
        except Exception as e:
            logging.warning(f"python-docx failed: {e}")

    # 3. Extract from plain text files (.txt)
    elif ext.endswith(".txt"):
        try:
            full_text = file_bytes.decode('utf-8')
            if full_text.strip():
                logging.info("Successfully extracted text from TXT file.")
                return full_text.strip()
        except Exception as e:
            logging.warning(f"Failed to read text file: {e}")

    # 4. Extract from Excel and CSV (.xlsx, .csv)
    elif ext.endswith(".xlsx") or ext.endswith(".csv"):
        try:
            if ext.endswith(".csv"):
                df = pd.read_csv(BytesIO(file_bytes))
            else:
                df = pd.read_excel(BytesIO(file_bytes))
            full_text = df.to_string(index=False)
            if full_text.strip():
                logging.info("Successfully extracted text from Excel/CSV.")
                return full_text.strip()
        except Exception as e:
            logging.warning(f"pandas failed to extract table: {e}")

    # 5. Extract from images (.png, .jpg, .jpeg) using Tesseract OCR
    elif ext.endswith((".png", ".jpg", ".jpeg")):
        if not TESSERACT_AVAILABLE:
            logging.error("Tesseract OCR not available. Cannot process images.")
            return ""
        
        try:
            logging.info("Extracting text from image using Tesseract OCR...")
            
            # Ensure Tesseract path is configured
            if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not pytesseract.pytesseract.tesseract_cmd:
                # Re-detect from env or PATH (Docker/Linux)
                retry_cmd = os.getenv("TESSERACT_CMD")
                if not retry_cmd:
                    try:
                        import shutil as _sh
                        retry_cmd = _sh.which("tesseract")
                    except Exception:
                        retry_cmd = None
                if retry_cmd and os.path.exists(retry_cmd):
                    pytesseract.pytesseract.tesseract_cmd = retry_cmd
                    logging.info(f"Configured Tesseract path: {retry_cmd}")
                # Ensure TESSDATA_PREFIX is set if available
                if 'TESSDATA_PREFIX' not in os.environ:
                    for candidate in [
                        '/usr/share/tesseract-ocr/4.00/tessdata',
                        '/usr/share/tesseract-ocr/tessdata'
                    ]:
                        if os.path.exists(candidate):
                            os.environ['TESSDATA_PREFIX'] = candidate
                            logging.info(f"Set TESSDATA_PREFIX to: {candidate}")
                            break

            image = Image.open(BytesIO(file_bytes))
            logging.info(f"Loaded image: mode={image.mode}, size={image.size}")
            
            # Store original image for comparison
            original_image = image.copy()
            
            # Try OCR with multiple preprocessing techniques
            from PIL import ImageEnhance, ImageFilter, ImageOps
            text = ""
            successful_config = None
            all_texts = []  # Collect all OCR results
            
            # Strategy 1: No preprocessing (original image)
            logging.info("Strategy 1: Trying OCR without preprocessing...")
            try:
                text = pytesseract.image_to_string(original_image, lang='eng')
                if text.strip():
                    logging.info(f"Strategy 1 succeeded! Extracted {len(text)} characters")
                    logging.info(f"First 300 chars: {text[:300]}")
                    all_texts.append(("no_preprocessing", text.strip()))
            except Exception as e:
                logging.warning(f"Strategy 1 failed: {e}")
            
            # Strategy 2: Enhanced preprocessing for better text extraction
            logging.info("Strategy 2: Trying with enhanced preprocessing...")
            try:
                # Convert to RGB if needed (some images may have different modes)
                if original_image.mode != 'RGB':
                    processed_image = original_image.convert('RGB')
                else:
                    processed_image = original_image.copy()
                
                # Convert to grayscale for better OCR
                if processed_image.mode != 'L':
                    processed_image = processed_image.convert('L')
                    logging.info("Converted to grayscale")
                
                # Apply multiple sharpening passes for better edge definition
                processed_image = processed_image.filter(ImageFilter.SHARPEN)
                processed_image = processed_image.filter(ImageFilter.SHARPEN)
                logging.info("Applied double sharpening filter")
                
                # Very strong contrast boost for faint text
                enhancer = ImageEnhance.Contrast(processed_image)
                processed_image = enhancer.enhance(3.0)  # Increased from 2.0 to 3.0
                logging.info("Applied very strong contrast boost (3.0x)")
                
                # Enhanced brightness for visibility
                enhancer = ImageEnhance.Brightness(processed_image)
                processed_image = enhancer.enhance(1.3)  # Increased from 1.2 to 1.3
                logging.info("Applied enhanced brightness boost")
                
                # Resize for better OCR quality (minimum 1500px on smallest side - increased)
                width, height = processed_image.size
                if min(width, height) < 1500:
                    scale = 1500 / min(width, height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logging.info(f"Resized to {new_width}x{new_height}")
                
                # Try OCR with multiple configs - more configs for better date extraction
                configs_to_try = [
                    '--oem 3 --psm 3',  # Fully automatic page segmentation (best for complex layouts)
                    '--oem 3 --psm 6',  # Uniform block of text
                    '--oem 3 --psm 11', # Sparse text (good for forms)
                    '--oem 3 --psm 4',  # Single column
                    '--oem 3 --psm 12', # Sparse text with OSD
                    '--oem 3 --psm 1',  # Automatic with OSD
                    '--oem 3 --psm 0',  # Orientation and script detection
                ]
                
                for config in configs_to_try:
                    try:
                        temp_text = pytesseract.image_to_string(processed_image, lang='eng', config=config)
                        if temp_text.strip():
                            logging.info(f"Strategy 2 succeeded with config '{config}'! Extracted {len(temp_text)} characters")
                            all_texts.append(("enhanced_preprocessing_" + config, temp_text.strip()))
                            if not text.strip() or len(temp_text) > len(text):
                                text = temp_text
                                successful_config = f"enhanced_preprocessing with {config}"
                    except Exception as e:
                        logging.debug(f"Config '{config}' failed: {e}")
            except Exception as e:
                logging.warning(f"Strategy 2 failed: {e}")
            
            # Strategy 3: Aggressive preprocessing for difficult documents
            logging.info("Strategy 3: Trying aggressive preprocessing...")
            try:
                # Start with original image
                if original_image.mode != 'RGB':
                    aggr_image = original_image.convert('RGB')
                else:
                    aggr_image = original_image.copy()
                
                # Convert to grayscale
                if aggr_image.mode != 'L':
                    aggr_image = aggr_image.convert('L')
                
                # Multiple sharpening passes for faint text
                aggr_image = aggr_image.filter(ImageFilter.SHARPEN)
                aggr_image = aggr_image.filter(ImageFilter.SHARPEN)
                logging.info("Applied double sharpening")
                
                # Extremely aggressive contrast for very faint/worn documents
                enhancer = ImageEnhance.Contrast(aggr_image)
                aggr_image = enhancer.enhance(4.0)  # Increased from 3.0 to 4.0
                logging.info("Applied extremely aggressive contrast enhancement (4.0x)")
                
                # Enhanced brightness
                enhancer = ImageEnhance.Brightness(aggr_image)
                aggr_image = enhancer.enhance(1.4)
                logging.info("Applied enhanced brightness boost")
                
                # Apply Unsharp Mask for better text clarity
                aggr_image = aggr_image.filter(ImageFilter.UnsharpMask(radius=3, percent=200, threshold=3))
                logging.info("Applied strong unsharp mask")
                
                # Resize aggressively for maximum quality
                width, height = aggr_image.size
                if min(width, height) < 2000:
                    scale = 2000 / min(width, height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    aggr_image = aggr_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logging.info(f"Resized aggressively to {new_width}x{new_height}")
                
                # Try with different OCR configs
                for config in ['--oem 3 --psm 6', '--oem 3 --psm 11', '--oem 3 --psm 3']:
                    try:
                        temp_text = pytesseract.image_to_string(aggr_image, lang='eng', config=config)
                        if temp_text.strip():
                            logging.info(f"Strategy 3 succeeded with config '{config}'! Extracted {len(temp_text)} characters")
                            all_texts.append(("aggressive_preprocessing_" + config, temp_text.strip()))
                            if not text.strip() or len(temp_text) > len(text):
                                text = temp_text
                                successful_config = f"aggressive_preprocessing with {config}"
                    except Exception as e:
                        logging.debug(f"Aggressive preprocessing with {config} failed: {e}")
            except Exception as e:
                logging.warning(f"Strategy 3 failed: {e}")
            
            # Strategy 4: Try with multi-language support (Hindi + English for Indian documents)
            logging.info("Strategy 4: Trying multi-language OCR (Hindi+English)...")
            try:
                # Use the best preprocessed image we have
                if 'processed_image' in locals():
                    test_image = processed_image
                else:
                    test_image = original_image
                    if test_image.mode != 'L':
                        test_image = test_image.convert('L')
                
                languages_to_try = ['hin+eng', 'eng+hin', 'eng']
                for lang in languages_to_try:
                    for config in ['--oem 3 --psm 6', '--oem 3 --psm 11']:
                        try:
                            temp_text = pytesseract.image_to_string(test_image, lang=lang, config=config)
                            if temp_text.strip():
                                logging.info(f"Multi-language OCR succeeded with '{lang}' and '{config}'! Extracted {len(temp_text)} characters")
                                all_texts.append(("multilang_" + lang + "_" + config, temp_text.strip()))
                                if not text.strip() or len(temp_text) > len(text):
                                    text = temp_text
                                    successful_config = f"multilang {lang} with {config}"
                        except Exception as e:
                            logging.debug(f"Multi-language OCR with {lang} and {config} failed: {e}")
            except Exception as e:
                logging.warning(f"Strategy 4 failed: {e}")
            
            # Select the best result (longest text)
            if all_texts:
                # Sort by length and get the longest
                all_texts.sort(key=lambda x: len(x[1]), reverse=True)
                best_strategy, best_text = all_texts[0]
                
                if best_text != text:
                    text = best_text
                    successful_config = best_strategy
                
                logging.info(f"Best OCR result: {best_strategy} with {len(best_text)} characters")
                logging.info(f"First 500 chars of best result: {best_text[:500]}")
            
            if successful_config:
                logging.info(f"Final successful OCR config: {successful_config}")
            else:
                logging.warning("All OCR attempts returned empty or failed")
            
            if text.strip():
                logging.info(f"Successfully extracted text from image using Tesseract OCR. Text length: {len(text)}")
                return text.strip()
            else:
                logging.warning("Tesseract OCR returned empty text after trying all configurations.")
                return ""
        except Exception as e:
            logging.error(f"Tesseract OCR error: {e}", exc_info=True)
            logging.error(traceback.format_exc())
            return ""

    # If all methods fail
    logging.error(f"Failed to extract text from file: {file_path}")
    return ""