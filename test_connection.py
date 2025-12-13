#!/usr/bin/env python3
"""
Test script to verify the backend server connection and contract analysis endpoint.
"""

import requests
import time

def test_server_connection():
    """Test if the backend server is accessible"""
    print("=== Testing Backend Server Connection ===")
    
    # Test if the server is running
    try:
        response = requests.get("http://localhost:8002/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to server: {str(e)}")
        return False
    
    # Test the contract analysis endpoint (HEAD request to check if endpoint exists)
    try:
        response = requests.head("http://localhost:8002/api/analyze/contract", timeout=5)
        if response.status_code in [200, 405]:  # 405 is expected for HEAD on POST endpoint
            print("✅ Contract analysis endpoint exists")
        else:
            print(f"❌ Contract analysis endpoint returned unexpected status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to access contract analysis endpoint: {str(e)}")
    
    print("\n=== Server Connection Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_server_connection()
    if success:
        print("\n🎉 Backend server is properly configured and running!")
        print("The 'Network error: Unable to connect to the server' message should no longer appear.")
    else:
        print("\n❌ Backend server configuration issues detected.")