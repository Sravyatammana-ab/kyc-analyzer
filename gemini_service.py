import os
import json
import logging
import asyncio
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except Exception as import_error:  # pragma: no cover
    genai = None
    logging.error(f"Failed to import google-generativeai: {import_error}")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _ensure_client_configured() -> None:
    if genai is None:
        raise RuntimeError("google-generativeai is not installed. Add 'google-generativeai' to requirements.txt")
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set in environment.")
    genai.configure(api_key=GEMINI_API_KEY)


def _get_model(response_mime_type: Optional[str] = None):
    _ensure_client_configured()
    generation_config = None
    if response_mime_type:
        generation_config = {"response_mime_type": response_mime_type}
    return genai.GenerativeModel(model_name=GEMINI_MODEL, generation_config=generation_config)


async def _run_blocking(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def classify_document(text: str) -> dict:
    """Classify document type using Gemini, returning {"document_type": str}."""
    logging.info("Classifying document type with Gemini...")
    prompt = (
        "Analyze the following text and respond ONLY with a JSON object containing a single "
        "'document_type' key. Choose from: 'Invoice', 'BalanceSheet', 'ProfitAndLossStatement', "
        "'Contract', 'GeneralDocument'. Example: {\"document_type\": \"Invoice\"}.\n\n" 
        + (text[:4000] if text else "")
    )
    model = _get_model(response_mime_type="application/json")

    def _invoke():
        return model.generate_content(prompt)

    response = await _run_blocking(_invoke)
    content = (response.text or "").strip()
    try:
        data = json.loads(content) if content else {}
        if isinstance(data, dict) and "document_type" in data:
            return {"document_type": data["document_type"]}
        return {"document_type": str(data) or "GeneralDocument"}
    except Exception as e:
        logging.warning(f"Gemini classification parse error: {e}; raw={content[:200]}")
        return {"document_type": "GeneralDocument"}


async def analyze_document_by_type(text: str, doc_type: str) -> dict:
    """Analyze document and return structured JSON summary using Gemini."""
    logging.info(f"Analyzing document with Gemini. Type hint: {doc_type}")
    system_instructions = (
        "You are an expert document analysis AI. Respond ONLY with a valid JSON object. "
        "Include: 'language', 'document_type', 1-3 sentence 'summary', and 'extracted_data'"
        " object with key-value pairs explicitly present in the text."
    )

    prompt = (
        f"Document type hint: {doc_type}.\n\n"
        "Analyze the following text. Return JSON in the structure:\n"
        "{\n  \"language\": \"English\",\n  \"document_type\": \"Invoice\",\n  \"summary\": \"...\",\n  \"extracted_data\": {\n    \"Invoice Number\": \"...\"\n  }\n}\n\n"
        + (text or "")
    )

    model = _get_model(response_mime_type="application/json")

    def _invoke():
        return model.generate_content([system_instructions, prompt])

    response = await _run_blocking(_invoke)
    content = (response.text or "").strip()
    try:
        data = json.loads(content) if content else {}
        if isinstance(data, dict):
            return data
        return {"analysis_output": str(data)}
    except Exception as e:
        logging.warning(f"Gemini analysis parse error: {e}; raw={content[:200]}")
        return {"error": "Failed to analyze document."}


async def extract_text_from_file(file_path: str, file_bytes: bytes, mime_type: Optional[str]) -> str:
    """Use Gemini Multimodal to extract raw text from a file (pdf, docx, xlsx, csv, images)."""
    logging.info(f"Extracting text with Gemini from file: {file_path}")
    model = _get_model()

    def _upload_and_generate():
        # For images, use direct content generation instead of file upload
        if file_bytes and mime_type and mime_type.startswith('image/'):
            from io import BytesIO
            from PIL import Image
            try:
                # Convert bytes to PIL Image
                image = Image.open(BytesIO(file_bytes))
                prompt = (
                    "Extract the plain textual content from this image. "
                    "Return ONLY the extracted text with no additional commentary."
                )
                resp = model.generate_content([prompt, image])
                return (resp.text or "").strip()
            except Exception as e:
                logging.error(f"Error processing image with PIL: {e}")
                return ""
        else:
            # For other file types, use file upload
            if file_bytes:
                from io import BytesIO
                file_obj = BytesIO(file_bytes)
                uploaded = genai.upload_file(path=file_obj, mime_type=mime_type)
            else:
                uploaded = genai.upload_file(path=file_path, mime_type=mime_type)
            prompt = (
                "Extract the plain textual content from the provided file. "
                "Return ONLY the extracted text with no additional commentary."
            )
            resp = model.generate_content([prompt, uploaded])
            return (resp.text or "").strip()

    try:
        text = await _run_blocking(_upload_and_generate)
        return text
    except Exception as e:
        logging.error(f"Gemini extract_text_from_file error: {e}")
        return ""


