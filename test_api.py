import urllib.request
import urllib.error
import json

def test_login():
    """Test admin login"""
    url = "http://localhost:8000/auth/login"
    data = json.dumps({"email": "admin@jobsify.com", "password": "admin123"}).encode()
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ Login Success: {result}")
            return result.get("access_token")
    except urllib.error.HTTPError as e:
        print(f"❌ Login Failed: {e.code} - {e.read().decode()}")
        return None

def test_admin_endpoint(endpoint, token=None):
    """Test admin endpoint with/without token"""
    url = f"http://localhost:8000{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = "Bearer null"
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ {endpoint}: {response.status} - Success")
            return True
    except urllib.error.HTTPError as e:
        error_msg = json.loads(e.read().decode())
        print(f"❌ {endpoint}: {e.code} - {error_msg}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING AUTHENTICATION FIXES")
    print("=" * 60)
    
    # Test 1: Login to get valid token
    print("\n1. Testing Admin Login...")
    token = test_login()
    
    if not token:
        print("❌ Cannot proceed without valid token")
        exit(1)
    
    # Test 2: Access admin endpoints with valid token
    print("\n2. Testing Admin Endpoints WITH Valid Token...")
    endpoints = [
        "/admin/stats",
        "/admin/users",
        "/admin/workers/pending",
        "/admin/reports/pending"
    ]
    
    for endpoint in endpoints:
        test_admin_endpoint(endpoint, token)
    
    # Test 3: Access admin endpoints with null token (should fail)
    print("\n3. Testing Admin Endpoints WITH NULL Token (Should Fail)...")
    for endpoint in endpoints:
        test_admin_endpoint(endpoint, None)
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
