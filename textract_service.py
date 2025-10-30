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
import time

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not installed. OCR functionality will be limited.")

load_dotenv()

# Configure a hard ceiling for OCR processing latency (seconds)
MAX_OCR_SECONDS = int(os.getenv("MAX_OCR_SECONDS", "55"))

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

    start_time = time.monotonic()

    # Log Tesseract status
    if TESSERACT_AVAILABLE:
        logging.info(f"Tesseract available: True, Path: {getattr(pytesseract.pytesseract, 'tesseract_cmd', 'Not configured')}")
    else:
        logging.warning("Tesseract NOT available - pytesseract not installed")

    def deadline_exceeded() -> bool:
        return (time.monotonic() - start_time) > MAX_OCR_SECONDS

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

        # Fallback to Tesseract for scanned PDFs (limited pages to honor deadline)
        if TESSERACT_AVAILABLE and not deadline_exceeded():
            try:
                logging.info("Attempting Tesseract OCR on PDF pages...")
                with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                    extracted_text = []
                    for page_num, page in enumerate(pdf.pages[:2]):  # limit to first 2 pages for latency
                        if deadline_exceeded():
                            break
                        try:
                            image = page.to_image(resolution=200)
                            text = pytesseract.image_to_string(image.original, lang='eng')
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
            logging.warning("Tesseract not available or deadline exceeded. Cannot perform OCR on scanned PDF.")

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

            # Ensure Tesseract path is configured (retry)
            if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not pytesseract.pytesseract.tesseract_cmd:
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
                if 'TESSDATA_PREFIX' not in os.environ:
                    for candidate in ['/usr/share/tesseract-ocr/4.00/tessdata','/usr/share/tesseract-ocr/tessdata']:
                        if os.path.exists(candidate):
                            os.environ['TESSDATA_PREFIX'] = candidate
                            logging.info(f"Set TESSDATA_PREFIX to: {candidate}")
                            break

            image = Image.open(BytesIO(file_bytes))
            logging.info(f"Loaded image: mode={image.mode}, size={image.size}")

            original_image = image.copy()

            from PIL import ImageEnhance, ImageFilter
            text = ""
            successful_config = None
            all_texts = []

            # Strategy 1: No preprocessing
            if not deadline_exceeded():
                try:
                    text = pytesseract.image_to_string(original_image, lang='eng')
                    if text.strip():
                        all_texts.append(("no_preprocessing", text.strip()))
                        successful_config = "no_preprocessing"
                except Exception as e:
                    logging.warning(f"Strategy 1 failed: {e}")

            # Strategy 2: Light preprocessing (single pass) and two configs
            if not text.strip() and not deadline_exceeded():
                try:
                    processed_image = original_image.convert('L') if original_image.mode != 'L' else original_image.copy()
                    processed_image = processed_image.filter(ImageFilter.SHARPEN)
                    width, height = processed_image.size
                    if min(width, height) < 1200:
                        scale = 1200 / min(width, height)
                        processed_image = processed_image.resize((int(width*scale), int(height*scale)), Image.Resampling.LANCZOS)
                    for config in ['--oem 3 --psm 6', '--oem 3 --psm 11']:
                        if deadline_exceeded():
                            break
                        try:
                            temp_text = pytesseract.image_to_string(processed_image, lang='eng', config=config)
                            if temp_text.strip():
                                all_texts.append(("light_preprocessing_"+config, temp_text.strip()))
                                if len(temp_text) > len(text):
                                    text = temp_text
                                    successful_config = f"light_preprocessing {config}"
                        except Exception:
                            pass
                except Exception as e:
                    logging.warning(f"Strategy 2 failed: {e}")

            if all_texts:
                all_texts.sort(key=lambda x: len(x[1]), reverse=True)
                best_strategy, best_text = all_texts[0]
                if best_text != text:
                    text = best_text
                    successful_config = best_strategy

            if text.strip():
                logging.info(f"Successfully extracted text from image. Strategy: {successful_config}, length: {len(text)}")
                return text.strip()
            else:
                logging.warning("OCR returned empty text after limited strategies.")
                return ""
        except Exception as e:
            logging.error(f"Tesseract OCR error: {e}", exc_info=True)
            logging.error(traceback.format_exc())
            return ""

    # If all methods fail
    logging.error(f"Failed to extract text from file: {file_path}")
    return ""