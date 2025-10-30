"""
Test script for the OpenAI KYC API
"""
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/analyze"

def test_health():
    """Test health endpoint"""
    response = requests.get("http://localhost:8000/health")
    print("Health Check:", response.json())
    assert response.status_code == 200

def test_analyze_document(file_path: str):
    """Test document analysis endpoint"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(API_URL, files=files)
    
    print(f"\nTesting file: {file_path}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*50)
        print("ANALYSIS RESULT")
        print("="*50)
        print(json.dumps(result, indent=2))
        print("="*50)
        
        # Check if validation dates are present for Passport/Driving Licence
        doc_type = result.get("document_type", "")
        if doc_type in ["Passport", "DrivingLicence"]:
            extracted_data = result.get("analysis", {}).get("extracted_data", {})
            if doc_type == "Passport":
                print("\n✓ Passport validation dates:")
                print(f"  - Issue Date: {extracted_data.get('Issue Date', 'N/A')}")
                print(f"  - Expiry Date: {extracted_data.get('Expiry Date', 'N/A')}")
            elif doc_type == "DrivingLicence":
                print("\n✓ Driving Licence validation dates:")
                print(f"  - Valid From: {extracted_data.get('Valid From', 'N/A')}")
                print(f"  - Valid Until: {extracted_data.get('Valid Until', 'N/A')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("Testing KYC Analysis API")
    print("-" * 50)
    
    # Test health endpoint
    try:
        test_health()
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the server is running: uvicorn main:app --reload")
        exit(1)
    
    # Test with a sample file (modify path as needed)
    # Uncomment the line below and provide a valid file path
    # test_analyze_document("path/to/your/kyc/document.pdf")
    
    print("\nTest script ready. Uncomment test_analyze_document line to test with actual files.")

