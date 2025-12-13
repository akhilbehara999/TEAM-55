import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.json()}")
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
    
    # Test health endpoint
    print("\nTesting health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Health endpoint response: {response.json()}")
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
    
    # Test API v1 root endpoint
    print("\nTesting API v1 root endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/")
        print(f"API v1 root endpoint status: {response.status_code}")
        print(f"API v1 root endpoint response: {response.json()}")
    except Exception as e:
        print(f"Error testing API v1 root endpoint: {e}")

if __name__ == "__main__":
    test_backend()