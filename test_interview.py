import requests
import json

try:
    response = requests.post(
        'http://localhost:8000/api/human_interview/start',
        json={
            'role': 'Senior Data Analyst',
            'experience_level': 'Beginner'
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")