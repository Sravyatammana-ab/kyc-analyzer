import os
import json
import logging
from typing import Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def _ensure_client_configured() -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")


async def classify_document(text: str) -> dict:
    """Classify KYC document type using OpenAI, returning {"document_type": str}."""
    logging.info("Classifying KYC document type with OpenAI...")
    _ensure_client_configured()
    
    prompt = (
        "Analyze the following OCR-extracted text from a KYC document. Identify what type of document this is based on the text content.\n\n"
        "Document types:\n"
        "- 'Passport': Contains passport number, issue date, expiry date, MRZ (machine readable zone), nationality, 'REPUBLIC OF', 'P<'\n"
        "- 'Aadhar': Contains 12-digit Aadhar number, 'Government of India', 'My Aadhar My Identity'\n"
        "- 'PAN': Contains 10-character alphanumeric PAN number, 'INCOME TAX DEPARTMENT'\n"
        "- 'DrivingLicence': Contains DL number, 'Driving Licence', vehicle classes, licence validity dates\n"
        "- 'UtilityBill': Contains account number, bill amount, service provider name, bill period\n"
        "- 'GeneralDocument': If none of the above match\n\n"
        "Respond ONLY with a JSON object containing a single 'document_type' key. Example: {\"document_type\": \"Passport\"}.\n\n"
        "OCR Text:\n" + (text[:4000] if text else "")
    )
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a KYC document classification expert. Analyze document characteristics to identify the type. Respond only with valid JSON with document_type field."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        data = json.loads(content) if content else {}
        
        if isinstance(data, dict) and "document_type" in data:
            classified_type = data["document_type"]
            logging.info(f"Document classified as: {classified_type}")
            return {"document_type": classified_type}
        
        logging.warning(f"Unexpected classification result: {data}")
        return {"document_type": str(data) or "GeneralDocument"}
    except Exception as e:
        logging.error(f"OpenAI classification error: {e}")
        return {"document_type": "GeneralDocument"}


async def analyze_document_by_type(text: str, doc_type: str) -> dict:
    """Analyze KYC document and return structured JSON summary using OpenAI."""
    logging.info(f"Analyzing KYC document with OpenAI. Type: {doc_type}")
    _ensure_client_configured()
    
    # Get specialized prompt based on document type
    prompt = _get_kyc_prompt(text, doc_type)
    
    # Log the extracted text for debugging
    logging.info(f"Extracted text length: {len(text)} characters")
    logging.info(f"First 500 characters of extracted text: {text[:500]}")
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert KYC document analysis AI. Respond only with valid JSON. Extract all key details accurately."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        data = json.loads(content) if content else {}
        
        if isinstance(data, dict):
            return data
        return {"error": "Failed to analyze document"}
    except Exception as e:
        logging.error(f"OpenAI analysis error: {e}")
        return {"error": str(e)}


def _get_kyc_prompt(text: str, doc_type: str) -> str:
    """Generate KYC-specific prompts based on document type."""
    
    base_prompt = (
        "You are an expert at extracting information from KYC documents. "
        "Analyze the following OCR-extracted text carefully and extract all visible key details. "
        "You MUST extract ONLY the fields specified in the JSON structure below. "
        "DO NOT add fields from other document types. "
        "Extract ALL specified fields - DO NOT skip any field. "
        "For fields like Gender, if you see a single letter M or F, extract it. "
        "If any required field is not found in the text, use \"Not provided\" as the value. "
        "Return ONLY a valid JSON object with the following structure:\n"
    )
    
    if doc_type == "PAN":
        return base_prompt + """{
  "language": "English",
  "document_type": "PAN",
  "summary": "Brief summary of the PAN card",
  "extracted_data": {
    "PAN Number": "...",
    "Name": "...",
    "Father's Name": "...",
    "Date of Birth": "...",
    "Signature": "..."
  }
}""" + "\n\nText:\n" + text
    
    elif doc_type == "Aadhar":
        return base_prompt + """{
  "language": "English",
  "document_type": "Aadhar",
  "summary": "Brief summary of the Aadhar card including holder name and key details",
  "extracted_data": {
    "Aadhar Number": "Extract the 12-digit Aadhar number (format: XXXX XXXX XXXX)",
    "Name": "Full name in both English and regional language if present",
    "Date of Birth": "Birth date in DD/MM/YYYY format",
    "Gender": "Male, Female, or Transgender",
    "Address": "Complete address if visible on front side"
  }
}

CRITICAL: This is an Aadhar card document. Extract ONLY Aadhar-specific fields. DO NOT extract passport, PAN, or any other document fields.
Look carefully for the Aadhar number - it is typically 12 digits in groups of 4 (e.g., 2895 1522 1385). Search the entire text for numbers matching this pattern.""" + "\n\nExtracted Text from Document:\n" + text
    
    elif doc_type == "DrivingLicence":
        return base_prompt + """{
  "language": "English",
  "document_type": "DrivingLicence",
  "summary": "Brief summary of the driving licence",
  "extracted_data": {
    "Licence Number": "...",
    "Name": "...",
    "Date of Birth": "...",
    "Valid From": "...",
    "Valid Until": "...",
    "Address": "...",
    "Vehicle Classes": "..."
  }
}""" + "\n\nText:\n" + text
    
    elif doc_type == "Passport":
        return base_prompt + """{
  "language": "English",
  "document_type": "Passport",
  "summary": "Brief summary of the passport including holder name and key details",
  "extracted_data": {
    "Passport Number": "Passport number (alphanumeric, e.g., W9699466)",
    "Name": "Full name including surname and given names",
    "Date of Birth": "Birth date in DD/MM/YYYY format",
    "Gender": "M, F, Male, or Female (often just M or F as a single letter)",
    "Place of Birth": "City and state/country of birth",
    "Issue Date": "Date of issue in DD/MM/YYYY format",
    "Expiry Date": "Date of expiry in DD/MM/YYYY format",
    "Place of Issue": "City/country where passport was issued",
    "Nationality": "Nationality (e.g., Indian, INDIAN)"
  }
}

CRITICAL: This is a Passport document. Extract ONLY passport-specific fields. DO NOT extract Aadhar or non-passport fields.

MANDATORY EXTRACTION: You MUST extract ALL fields listed above. Every single field is required. DO NOT skip Date of Birth or Gender. These fields are CRITICAL.
Search the ENTIRE text carefully from beginning to end. Look for:
REQUIRED FIELDS:
- Passport numbers (typically alphanumeric like W9699466)
- Issue dates and expiry dates in DD/MM/YYYY or DD-MM-YYYY format (e.g., 27/12/2022, 26/12/2032)
- Places of issue and birth
- Names in all caps
- The passport number may appear in the MRZ (Machine Readable Zone) section.
Pay special attention to dates - search for patterns like DD/MM/YYYY throughout the text.

SPECIFIC EXTRACTION INSTRUCTIONS FOR MISSING FIELDS:

Date of Birth - REQUIRED: Search for labels "DOB", "Date of Birth", "Birth:" followed by DD/MM/YYYY format dates. Example: 10/02/2002 or 10/04/2002

Gender - ABSOLUTELY REQUIRED: This field is MANDATORY. The Gender field is critical for passport analysis.
- Search for "Sex:" label followed by M or F
- The value is often just a single letter: M (for Male) or F (for Female)
- Look for "Sex: M", "Sex:F", "Sex : M", "Sex : F"
- Also look for standalone uppercase "M" or "F" appearing in the text
- The letter "M" alone means Male, "F" alone means Female
- Extract the letter M or F even if it's just one character
- If you find "M" anywhere in the text near date fields, extract it as "M" or "Male"
- DO NOT return "Not provided" for Gender - this field MUST be extracted if present

VALIDATION: After extraction, verify you have extracted Gender. If not, search the entire text again looking specifically for the letters M or F.""" + "\n\nExtracted Text from Document:\n" + text
    
    elif doc_type == "UtilityBill":
        return base_prompt + """{
  "language": "English",
  "document_type": "UtilityBill",
  "summary": "Brief summary of the utility bill",
  "extracted_data": {
    "Account Number": "...",
    "Name": "...",
    "Address": "...",
    "Bill Date": "...",
    "Bill Amount": "...",
    "Service Type": "..."
  }
}""" + "\n\nText:\n" + text
    
    else:
        # General document
        return base_prompt + """{
  "language": "English",
  "document_type": "GeneralDocument",
  "summary": "Brief summary of the document",
  "extracted_data": {
    "Key1": "Value1",
    "Key2": "Value2"
  }
}""" + "\n\nText:\n" + text
