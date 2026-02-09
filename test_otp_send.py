import requests
import json

# Test registration to check if OTP is sent
BASE_URL = "http://localhost:8001"

def test_register():
    url = f"{BASE_URL}/auth/register"
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123",
        "phone": "1234567890"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("Registration successful. Check backend logs for OTP email send status.")
        else:
            print("Registration failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
