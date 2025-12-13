import requests
import json

# Read the test resume content
with open('test_resume.txt', 'r') as f:
    resume_content = f.read()

# Test the resume analysis endpoint
url = 'http://localhost:8001/api/analyze/resume/text'
headers = {'Content-Type': 'application/json'}

data = {
    "resume_content": resume_content,
    "job_description": "Senior Software Engineer position requiring Python and cloud experience"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")