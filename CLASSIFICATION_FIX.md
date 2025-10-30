# Document Classification Fix

## Problem Identified

Passport images were being classified as "Aadhar" and showing Aadhar-specific fields in the analysis results.

**Example Issue:**
- Input: Passport image with passport number "W9699466"
- Classification: "Aadhar" (WRONG)
- Analysis: Showing "Aadhar Number" field instead of "Passport Number", "Issue Date", "Expiry Date" fields

## Root Cause

### Classification Prompt Was Too Generic
The classification prompt didn't provide enough context about what defines each document type. It was:
```python
"Analyze the following text and respond ONLY with a JSON object containing a single 'document_type' key."
```

This gave no guidance on how to differentiate between document types based on content.

### Analysis Prompts Didn't Enforce Field Restrictions
While prompts defined which fields to extract, they didn't strongly enforce NOT mixing fields from other document types.

## Solutions Applied

### 1. Enhanced Classification Prompt (`openai_service.py` lines 28-39)

**Before:**
```python
prompt = (
    "Analyze the following text and respond ONLY with a JSON object containing a single "
    "'document_type' key. Choose from: 'PAN', 'Aadhar', 'DrivingLicence', 'Passport', "
    "'UtilityBill', 'GeneralDocument'. Example: {\"document_type\": \"PAN\"}.\n\n" 
    + (text[:4000] if text else "")
)
```

**After:**
```python
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
```

**Key Improvements:**
- Lists specific keywords and characteristics for each document type
- Passport: specifically mentions "passport number", "MRZ", "REPUBLIC OF", "P<"
- Aadhar: mentions 12-digit number pattern and government text
- Each type has unique identifiers to help classification

### 2. Improved System Message for Classification (line 45)

**Before:**
```python
{"role": "system", "content": "You are a KYC document classification expert. Respond only with valid JSON."}
```

**After:**
```python
{"role": "system", "content": "You are a KYC document classification expert. Analyze document characteristics to identify the type. Respond only with valid JSON with document_type field."}
```

**Key Improvements:**
- Emphasizes "Analyze document characteristics"
- More specific instructions

### 3. Lower Temperature for More Consistent Classification (line 49)

**Before:**
```python
temperature=0.3
```

**After:**
```python
temperature=0.1
```

**Reason:** Lower temperature (0.1) makes responses more deterministic and consistent, which is better for classification tasks.

### 4. Enhanced Field Restrictions in Analysis Prompts

#### Base Prompt (lines 100-107)
**Before:**
```python
base_prompt = "You are an expert at extracting information from KYC documents. Analyze the following OCR-extracted text carefully and extract all visible key details. Return ONLY a valid JSON object with the following structure. If any field is not found in the text, use \"Not provided\" as the value:\n"
```

**After:**
```python
base_prompt = (
    "You are an expert at extracting information from KYC documents. "
    "Analyze the following OCR-extracted text carefully and extract all visible key details. "
    "You MUST extract ONLY the fields specified in the JSON structure below. "
    "DO NOT add fields from other document types. "
    "If any required field is not found in the text, use \"Not provided\" as the value. "
    "Return ONLY a valid JSON object with the following structure:\n"
)
```

**Key Improvements:**
- Explicitly states "MUST extract ONLY the fields specified"
- Warns "DO NOT add fields from other document types"

#### Aadhar Prompt (line 130)
**Added:**
```
CRITICAL: This is an Aadhar card document. Extract ONLY Aadhar-specific fields. DO NOT extract passport, PAN, or any other document fields.
```

#### Passport Prompt (line 167)
**Added:**
```
CRITICAL: This is a Passport document. Extract ONLY passport-specific fields like Passport Number, Issue Date, Expiry Date, Place of Issue. DO NOT extract Aadhar number or any non-passport fields.
```

### 5. Enhanced Logging

Added detailed logging to track classification:
- Extract text preview (first 300 chars)
- Classification result
- Document type identified
- Proceeding with analysis message

This helps debug misclassification issues.

## Expected Results

### Before Fix
```json
{
  "filename": "manoj passport front.jpg",
  "document_type": "Aadhar",
  "analysis": {
    "document_type": "Aadhar",
    "extracted_data": {
      "Aadhar Number": "Not provided",
      "Name": "Mano Kumar Chimmula",
      "Gender": "Not provided"
    }
  }
}
```

### After Fix (Expected)
```json
{
  "filename": "manoj passport front.jpg",
  "document_type": "Passport",
  "analysis": {
    "document_type": "Passport",
    "summary": "This is an Indian passport issued to Chimmula Manojkumar, born on 10/02/2002...",
    "extracted_data": {
      "Passport Number": "W9699466",
      "Name": "CHIMMULA MANOJKUMAR",
      "Date of Birth": "10/02/2002",
      "Gender": "Male",
      "Place of Birth": "MANUGURU, TELANGANA",
      "Issue Date": "27/12/2022",
      "Expiry Date": "26/12/2032",
      "Place of Issue": "HYDERABAD",
      "Nationality": "INDIAN"
    }
  }
}
```

## Files Modified

1. **openai_service.py** (lines 23-61, 97-167)
   - Enhanced classification prompt with document characteristics
   - Improved base prompt with field restrictions
   - Added CRITICAL warnings for field-specific extraction
   - Lower temperature for consistency
   - Enhanced logging

2. **main.py** (lines 81-91)
   - Added detailed logging for classification and analysis flow

## Testing Instructions

1. **Restart server**: `uvicorn main:app --reload`
2. **Test passport**: Upload "manoj passport front.jpg"
3. **Verify classification**: Check logs for "Document classified as: Passport"
4. **Verify fields**: Ensure passport-specific fields are extracted
5. **Test Aadhar**: Upload "komal aadhar front.jpg"
6. **Verify classification**: Check logs for "Document classified as: Aadhar"
7. **Verify fields**: Ensure Aadhar-specific fields are extracted

## Success Criteria

✅ Passport classified as "Passport" (not "Aadhar")  
✅ Passport fields: Passport Number, Issue Date, Expiry Date, etc.  
✅ Aadhar classified as "Aadhar"  
✅ Aadhar fields: Aadhar Number, Name, DOB, Gender  
✅ No field mixing between document types  
✅ Logs show classification process  

## Troubleshooting

### If passport still misclassified:
1. Check OCR text in logs (first 300 chars)
2. Look for keywords: "passport number", "REPUBLIC OF", "MRZ"
3. Verify OCR is extracting passport-specific text
4. May need to improve OCR preprocessing

### If fields still mixed:
1. Check which document type was classified
2. Verify the analysis prompt was used for correct type
3. Look for "CRITICAL" warnings in logs
4. May need to strengthen field restrictions further

