import requests
import json

BASE_URL = "http://localhost:8001"

def test_registration():
    # Test data
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ Registration successful")
        else:
            print("❌ Registration failed")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_invalid_phone():
    # Test with invalid phone
    test_data = {
        "name": "Test User2",
        "email": "test2@example.com",
        "password": "password123",
        "phone": "12345"  # Invalid phone
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 422:  # Pydantic validation error
            print("✅ Invalid phone validation working")
        else:
            print("❌ Invalid phone validation failed")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing registration with phone...")
    test_registration()
    print("\nTesting invalid phone...")
    test_invalid_phone()
