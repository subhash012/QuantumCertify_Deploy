#!/usr/bin/env python3
"""
Test the health endpoint directly
"""
import sys
import os
sys.path.append('.')

try:
    from app.main import app
    from fastapi.testclient import TestClient
    
    # Create test client
    client = TestClient(app)
    
    print("Testing health endpoint...")
    
    # Test the health endpoint
    response = client.get("/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code != 200:
        print(f"ERROR: Health endpoint returned {response.status_code} instead of 200")
        print("This explains why Railway healthcheck is failing!")
    else:
        print("SUCCESS: Health endpoint working correctly")

except Exception as e:
    print(f"Error testing health endpoint: {e}")
    import traceback
    traceback.print_exc()