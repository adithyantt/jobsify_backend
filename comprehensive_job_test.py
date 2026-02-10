import requests

def test_jobs_endpoints():
    base_url = "http://10.13.1.105:8000"

    print("=== COMPREHENSIVE JOBS API TESTING ===\n")

    # Test 1: Get all verified jobs
    print("1. Testing GET /jobs (all verified jobs)")
    try:
        response = requests.get(f"{base_url}/jobs", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   Found {len(jobs)} verified jobs")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    print()

    # Test 2: Get my jobs with the email from logs
    print("2. Testing GET /jobs/my with actual email from logs")
    email = "vivekkrishna960@gmail.com"
    try:
        response = requests.get(f"{base_url}/jobs/my?email={email}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   Found {len(jobs)} jobs for {email}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    print()

    # Test 3: Get my jobs with test email
    print("3. Testing GET /jobs/my with test email")
    email = "test@example.com"
    try:
        response = requests.get(f"{base_url}/jobs/my?email={email}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"   Found {len(jobs)} jobs for {email}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    print()

    # Test 4: Edge case - empty email
    print("4. Testing GET /jobs/my with empty email")
    try:
        response = requests.get(f"{base_url}/jobs/my?email=", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    print()

    # Test 5: Edge case - invalid email (no @)
    print("5. Testing GET /jobs/my with invalid email")
    try:
        response = requests.get(f"{base_url}/jobs/my?email=invalidemail", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    print()

    # Test 6: Create a new job (if needed for further testing)
    print("6. Testing POST /jobs (create job)")
    job_data = {
        "title": "Test Job from API",
        "category": "Testing",
        "description": "This is a test job created via API",
        "location": "Test Location",
        "phone": "1234567890",
        "latitude": "0.0",
        "longitude": "0.0",
        "user_email": "test@example.com",
        "urgent": False,
        "salary": "100"
    }
    try:
        response = requests.post(f"{base_url}/jobs", json=job_data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            job = response.json()
            print(f"   Created job with ID: {job.get('id')}")
            new_job_id = job.get('id')
        else:
            print(f"   Error: {response.text}")
            new_job_id = None
    except Exception as e:
        print(f"   Exception: {e}")
        new_job_id = None
    print()

    # Test 7: Update the created job (if created)
    if new_job_id:
        print(f"7. Testing PUT /jobs/{new_job_id} (update job)")
        update_data = {
            "title": "Updated Test Job",
            "category": "Testing",
            "description": "Updated description",
            "location": "Updated Location",
            "phone": "0987654321",
            "latitude": "1.0",
            "longitude": "1.0",
            "user_email": "test@example.com",
            "urgent": True,
            "salary": "200"
        }
        try:
            response = requests.put(f"{base_url}/jobs/{new_job_id}?email=test@example.com", json=update_data, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   Job updated successfully")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        print()

        # Test 8: Delete the created job
        print(f"8. Testing DELETE /jobs/{new_job_id} (delete job)")
        try:
            response = requests.delete(f"{base_url}/jobs/{new_job_id}?email=test@example.com", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   Job deleted successfully")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        print()

    print("=== TESTING COMPLETE ===")

if __name__ == "__main__":
    test_jobs_endpoints()
