import requests
import sys

BASE_URL = "http://172.22.39.105:8000"
EMAIL = "vivekkrishna960@gmail.com"

def test_jobs_my():
    """Test /jobs/my endpoint"""
    print("\n" + "="*60)
    print("Testing /jobs/my endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/jobs/my", params={"email": EMAIL}, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Found {len(data)} jobs")
            if data:
                print(f"   First job: {data[0].get('title', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED! Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_workers_my():
    """Test /workers/my endpoint"""
    print("\n" + "="*60)
    print("Testing /workers/my endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/workers/my", params={"email": EMAIL}, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Found {len(data)} workers")
            if data:
                print(f"   First worker: {data[0].get('name', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED! Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_job_by_id():
    """Test /jobs/{id} endpoint still works"""
    print("\n" + "="*60)
    print("Testing /jobs/{id} endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/jobs/1", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is OK if job doesn't exist
            print(f"✅ SUCCESS! Endpoint is accessible")
            return True
        else:
            print(f"❌ FAILED! Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_worker_by_id():
    """Test /workers/{id} endpoint still works"""
    print("\n" + "="*60)
    print("Testing /workers/{id} endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/workers/1", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is OK if worker doesn't exist
            print(f"✅ SUCCESS! Endpoint is accessible")
            return True
        else:
            print(f"❌ FAILED! Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing API Route Fixes")
    print("Make sure the backend server is running!")
    
    results = []
    results.append(test_jobs_my())
    results.append(test_workers_my())
    results.append(test_job_by_id())
    results.append(test_worker_by_id())
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The route ordering fix is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please check the backend server status.")
        sys.exit(1)
