# OCR Enhancement V2 - Date Extraction Fix

## Problem

Passport expiry date "26/12/2032" was showing as "Not provided" despite being clearly visible in the document image.

## Root Cause

The OCR preprocessing wasn't aggressive enough for faint/blue-tinted ghost images and security features commonly found in passports. The contrast and brightness weren't sufficient to make the date text readable by Tesseract OCR.

## Solutions Applied

### 1. Increased Contrast and Brightness (textract_service.py)

#### Strategy 2: Enhanced Preprocessing
**Before:**
- Contrast: 2.0x
- Brightness: 1.2x
- Sharpening: 1 pass
- Resize: 1200px minimum

**After:**
- Contrast: **3.0x** (increased from 2.0x)
- Brightness: **1.3x** (increased from 1.2x)
- Sharpening: **2 passes** (double sharpening)
- Resize: **1500px minimum** (increased from 1200px)

#### Strategy 3: Aggressive Preprocessing
**Before:**
- Contrast: 3.0x
- Brightness: N/A
- Unsharp mask: radius=2, percent=150%
- Resize: 1500px minimum

**After:**
- Contrast: **4.0x** (increased from 3.0x)
- Brightness: **1.4x** (new)
- Sharpening: **2 passes** (double sharpening)
- Unsharp mask: **radius=3, percent=200%** (stronger)
- Resize: **2000px minimum** (increased from 1500px)

### 2. More OCR Configurations

Added more Page Segmentation Mode (PSM) configurations:
- PSM 0: Orientation and script detection
- PSM 1: Automatic with OSD
- PSM 3: Fully automatic (prioritized)
- PSM 4: Single column
- PSM 6: Uniform block
- PSM 11: Sparse text
- PSM 12: Sparse text with OSD

This ensures all possible text layouts are attempted.

### 3. Enhanced Prompt for Date Extraction (openai_service.py)

**Before:**
```
Carefully extract all passport details from the text. Look for passport numbers...
```

**After:**
```
Carefully extract all passport details from the text. Look for:
- Passport numbers (typically alphanumeric like W9699466)
- Issue dates and expiry dates in DD/MM/YYYY or DD-MM/YYYY format (e.g., 27/12/2022, 26/12/2032)
- Places of issue and birth
- Names in all caps
- The passport number may appear in the MRZ (Machine Readable Zone) section.
Pay special attention to dates - search for patterns like DD/MM/YYYY throughout the text.
```

Added specific date format examples and emphasized searching throughout the text.

## Expected Results

### Before Fix
```json
{
  "Expiry Date": "Not provided"
}
```

### After Fix
```json
{
  "Expiry Date": "26/12/2032"
}
```

## Technical Details

### Contrast Enhancement Logic
- **2.0x**: Standard contrast boost for normal documents
- **3.0x**: Strong boost for faint text (Strategy 2)
- **4.0x**: Maximum boost for extremely faint/worn documents (Strategy 3)

### Brightness Enhancement Logic
- **1.2x**: Standard brightness
- **1.3x**: Enhanced brightness (Strategy 2)
- **1.4x**: Strong brightness for maximum visibility (Strategy 3)

### Sharpening
- Single pass: Enhances edges
- Double pass: More aggressive edge definition for very faint text

### Unsharp Mask
- Before: radius=2, percent=150%
- After: radius=3, percent=200%
- Purpose: Further enhance text edges after contrast/brightness

### Resolution Scaling
- Higher resolution (1500px, 2000px) = more pixels for OCR to analyze
- Helps with small fonts and faint text
- Better for security features and ghost images

## Files Modified

1. **textract_service.py** (lines 186-286)
   - Strategy 2: Enhanced preprocessing
   - Strategy 3: Aggressive preprocessing
   - Added more OCR configs

2. **openai_service.py** (lines 178-185)
   - Enhanced date extraction prompt

3. **OCR_ENHANCEMENT_V2.md** (this file)
   - Documentation

## Testing Instructions

1. **Restart server**: `uvicorn main:app --reload`
2. **Test with passport**: Upload "manoj passport front.jpg"
3. **Verify expiry date**: Should show "26/12/2032" instead of "Not provided"
4. **Check logs**: Look for which OCR strategy succeeded
5. **Verify all fields**: Issue date, expiry date, gender, etc.

## Success Criteria

✅ Expiry date "26/12/2032" extracted  
✅ Issue date "27/12/2022" extracted  
✅ All passport fields populated  
✅ OCR strategies attempted with higher contrast/brightness  
✅ Logs show enhanced preprocessing applied  

## Troubleshooting

### If expiry date still "Not provided":

1. **Check OCR extracted text in logs**
   - Look for first 500 characters
   - Search for "26/12/2032" pattern
   - May be extracted but in different format

2. **Verify image quality**
   - Image should be clear
   - Avoid heavy compression
   - Minimum 800x800 pixels recommended

3. **Check which strategy succeeded**
   - Logs will show "Best OCR result: strategy_X"
   - Prefer strategies 2 or 3 (enhanced/aggressive)

4. **Try manual OCR test**:
   ```python
   from PIL import Image
   import pytesseract
   
   img = Image.open('manoj passport front.jpg')
   # Apply same preprocessing
   text = pytesseract.image_to_string(img)
   print(text)
   ```

5. **Image-specific issues**
   - Ghost images can interfere with OCR
   - Security features may obscure text
   - Try different angles/lighting when capturing

## Additional Notes

- Higher contrast/brightness may cause noise in some images
- System automatically tries multiple strategies and picks best
- Longer text extraction is generally better (more complete)
- Date format variations (DD/MM/YYYY vs DD-MM-YYYY) are handled

## Next Steps

If expiry date extraction still fails:
1. Review actual OCR output
2. Consider binarization (convert to pure black/white)
3. Try manual image preprocessing
4. Adjust preprocessing parameters based on image characteristics

