#!/usr/bin/env python3
"""
Test script for the Multi-Modal RAG application.
Run this script to test basic functionality.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_FILE = "sample_docs/sample.txt"

def test_api_health():
    """Test if the API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print("❌ API Health Check: FAILED")
            print(f"   Status Code: {response.status_code}")
            return False
    except Exception as e:
        print("❌ API Health Check: FAILED")
        print(f"   Error: {str(e)}")
        return False

def test_file_upload():
    """Test file upload functionality."""
    try:
        if not Path(TEST_FILE).exists():
            print("❌ File Upload Test: SKIPPED (test file not found)")
            return None
        
        with open(TEST_FILE, 'rb') as f:
            files = {'file': (TEST_FILE, f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File Upload Test: PASSED")
            print(f"   File ID: {result['file_id']}")
            print(f"   Message: {result['message']}")
            return result['file_id']
        else:
            print("❌ File Upload Test: FAILED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print("❌ File Upload Test: FAILED")
        print(f"   Error: {str(e)}")
        return None

def test_query(file_id):
    """Test query functionality."""
    if not file_id:
        print("❌ Query Test: SKIPPED (no file ID)")
        return False
    
    try:
        query_data = {
            "question": "What are the main topics in this document?",
            "file_id": file_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            headers={"Content-Type": "application/json"},
            data=json.dumps(query_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query Test: PASSED")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Sources: {len(result['sources'])} found")
            return True
        else:
            print("❌ Query Test: FAILED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print("❌ Query Test: FAILED")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Multi-Modal RAG Application")
    print("=" * 50)
    
    # Test 1: API Health
    if not test_api_health():
        print("\n❌ API is not accessible. Make sure the backend is running.")
        print("   Run: docker-compose up --build")
        return
    
    print()
    
    # Test 2: File Upload
    file_id = test_file_upload()
    
    print()
    
    # Test 3: Query
    test_query(file_id)
    
    print()
    print("🎉 Testing completed!")
    print("\nNext steps:")
    print("1. Open http://localhost:8501 for the Streamlit UI")
    print("2. Open http://localhost:8000/docs for API documentation")
    print("3. Try uploading different file types and asking questions")

if __name__ == "__main__":
    main()
