import os
import asyncio
import gemini_service

async def test_gemini():
    try:
        # Test the Gemini service
        result = await gemini_service.classify_document("This is a test invoice document.")
        print("Gemini classification test:", result)
        
        result2 = await gemini_service.analyze_document_by_type("This is a test invoice document.", "Invoice")
        print("Gemini analysis test:", result2)
        
    except Exception as e:
        print("Gemini error:", str(e))
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_gemini())
