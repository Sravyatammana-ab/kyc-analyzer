import requests
import os

# Test the analyze endpoint
url = "http://127.0.0.1:8000/analyze"

# Create a simple test file
test_content = "This is a test invoice.\nInvoice Number: INV-001\nAmount: $100.00"

try:
    # Test with a simple text file
    files = {'file': ('test.txt', test_content, 'text/plain')}
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")
