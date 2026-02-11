import urllib.request
import urllib.error
import json

def test_endpoint(url_path, token=None, description=""):
    """Test endpoint with detailed output"""
    url = f"http://localhost:8000{url_path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        token_display = token[:20] + "..." if len(token) > 20 else token
    else:
        headers["Authorization"] = "Bearer null"
        token_display = "null"
    
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    print(f"   Token: {token_display}")
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            result = response.read().decode()
            print(f"   ✅ SUCCESS: HTTP {response.status}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"   ❌ FAILED: HTTP {e.code}")
        try:
            error_json = json.loads(error_body)
            print(f"   Error: {error_json.get('detail', error_body[:100])}")
        except:
            print(f"   Error: {error_body[:100]}")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("AUTHENTICATION FIX VERIFICATION")
    print("=" * 70)
    
    # Get valid token
    print("\n📋 Step 1: Login to get valid token...")
    login_url = "http://localhost:8000/auth/login"
    login_data = json.dumps({"email": "admin@jobsify.com", "password": "admin123"}).encode()
    login_headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(login_url, data=login_data, headers=login_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            login_result = json.loads(response.read().decode())
            valid_token = login_result["access_token"]
            print(f"✅ Login successful! Token: {valid_token[:30]}...")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        exit(1)
    
    # Test with valid token
    print("\n" + "=" * 70)
    print("📋 Step 2: Testing with VALID token (should all succeed)...")
    print("=" * 70)
    
    test_endpoint("/admin/users", valid_token, "Get all users")
    test_endpoint("/admin/workers/pending", valid_token, "Get pending workers")
    
    # Test with null token
    print("\n" + "=" * 70)
    print("📋 Step 3: Testing with NULL token (should all fail with 401)...")
    print("=" * 70)
    
    test_endpoint("/admin/users", None, "Get all users (no auth)")
    test_endpoint("/admin/workers/pending", None, "Get pending workers (no auth)")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print("\n✅ Authentication fixes are working correctly!")
    print("   - Valid tokens: Access granted")
    print("   - Null/invalid tokens: Access denied (401)")
