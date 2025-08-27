import requests

# Correct Flask API chat endpoint
url = "http://127.0.0.1:5000/api/chat"

# Data with 'question' key expected by the Flask API
data = {
    "question": "Hello, are you working?"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Text:", response.text)  # Raw response for debugging

try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Failed to parse JSON response:", str(e))
