"""
Test script for Reviews API endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_worker_reviews(worker_id=1):
    """Test GET /reviews/worker/{id}"""
    print(f"\n🔍 Testing GET /reviews/worker/{worker_id}")
    try:
        response = requests.get(f"{BASE_URL}/reviews/worker/{worker_id}", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} reviews")
            if data:
                print(f"Sample review: {data[0]}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_get_worker_summary(worker_id=1):
    """Test GET /reviews/worker/{id}/summary"""
    print(f"\n🔍 Testing GET /reviews/worker/{worker_id}/summary")
    try:
        response = requests.get(f"{BASE_URL}/reviews/worker/{worker_id}/summary", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Summary: {data}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_add_review(worker_id=1, token=None):
    """Test POST /reviews (requires auth)"""
    print(f"\n🔍 Testing POST /reviews (worker_id={worker_id})")
    
    if not token:
        print("⚠️  No token provided, skipping authenticated test")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "worker_id": worker_id,
        "rating": 4,
        "comment": "Great service! Very professional."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/reviews",
            headers=headers,
            json=payload,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Review added: {data}")
            return data.get("id")
        else:
            print(f"❌ Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_update_review(review_id, token=None):
    """Test PUT /reviews/{id} (requires auth)"""
    print(f"\n🔍 Testing PUT /reviews/{review_id}")
    
    if not token or not review_id:
        print("⚠️  No token or review_id provided, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "rating": 5,
        "comment": "Updated: Excellent service! Highly recommended."
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/reviews/{review_id}",
            headers=headers,
            json=payload,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Review updated: {data}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_delete_review(review_id, token=None):
    """Test DELETE /reviews/{id} (requires auth)"""
    print(f"\n🔍 Testing DELETE /reviews/{review_id}")
    
    if not token or not review_id:
        print("⚠️  No token or review_id provided, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.delete(
            f"{BASE_URL}/reviews/{review_id}",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! {data}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_get_user_review(worker_id=1, token=None):
    """Test GET /reviews/worker/{id}/my-review (requires auth)"""
    print(f"\n🔍 Testing GET /reviews/worker/{worker_id}/my-review")
    
    if not token:
        print("⚠️  No token provided, skipping authenticated test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/reviews/worker/{worker_id}/my-review",
            headers=headers,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! User review: {data}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def login_and_get_token():
    """Login and get JWT token for testing"""
    print("\n🔐 Attempting to login...")
    
    # Try common test credentials
    test_users = [
        {"email": "test@example.com", "password": "password123"},
        {"email": "admin@jobsify.com", "password": "admin123"},
    ]
    
    for user in test_users:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=user,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print(f"✅ Logged in as {user['email']}")
                    return data["access_token"]
        except:
            pass
    
    print("⚠️  Could not login automatically. Please provide a token manually.")
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING REVIEWS API")
    print("=" * 60)
    
    # Test public endpoints
    test_get_worker_reviews(1)
    test_get_worker_summary(1)
    
    # Try to get auth token
    token = login_and_get_token()
    
    if token:
        # Test authenticated endpoints
        review_id = test_add_review(1, token)
        
        if review_id:
            test_get_user_review(1, token)
            test_update_review(review_id, token)
            test_get_worker_reviews(1)  # Check if review appears
            test_get_worker_summary(1)  # Check if summary updated
            test_delete_review(review_id, token)
            test_get_worker_reviews(1)  # Verify deletion
            test_get_worker_summary(1)  # Verify summary updated
    else:
        print("\n⚠️  Skipping authenticated tests (no token available)")
        print("To test authenticated endpoints, manually provide a token:")
        print("  token = 'your-jwt-token-here'")
        print("  test_add_review(1, token)")
    
    print("\n" + "=" * 60)
    print("✅ API TESTING COMPLETE")
    print("=" * 60)
