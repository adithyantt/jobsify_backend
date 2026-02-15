#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_saved_jobs_api():
    """Test the saved jobs API endpoints."""

    print("🧪 Testing Saved Jobs API Endpoints")
    print("=" * 50)

    # Test data
    test_user_email = "test@example.com"
    test_job_id = 1

    try:
        # 1. Test SAVE JOB
        print("\n1. Testing SAVE JOB endpoint...")
        save_payload = {
            "user_email": test_user_email,
            "job_id": test_job_id
        }

        response = requests.post(
            f"{BASE_URL}/jobs/save",
            json=save_payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Save job successful")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Save job failed: {response.text}")
            return False

        # 2. Test CHECK IF JOB IS SAVED
        print("\n2. Testing CHECK IF JOB IS SAVED endpoint...")
        response = requests.get(
            f"{BASE_URL}/jobs/saved/{test_job_id}?email={test_user_email}"
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("is_saved") == True:
                print("✅ Job is correctly marked as saved")
            else:
                print("❌ Job should be saved but is not")
                return False
        else:
            print(f"❌ Check saved job failed: {response.text}")
            return False

        # 3. Test GET SAVED JOBS
        print("\n3. Testing GET SAVED JOBS endpoint...")
        response = requests.get(
            f"{BASE_URL}/jobs/saved?email={test_user_email}"
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            saved_jobs = response.json()
            print(f"✅ Retrieved {len(saved_jobs)} saved jobs")
            if len(saved_jobs) > 0:
                print(f"Sample job: {saved_jobs[0]['title']}")
        else:
            print(f"❌ Get saved jobs failed: {response.text}")
            return False

        # 4. Test UNSAVE JOB
        print("\n4. Testing UNSAVE JOB endpoint...")
        response = requests.delete(
            f"{BASE_URL}/jobs/save/{test_job_id}?email={test_user_email}",
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Unsave job successful")
        else:
            print(f"❌ Unsave job failed: {response.text}")
            return False

        # 5. Verify job is no longer saved
        print("\n5. Verifying job is no longer saved...")
        response = requests.get(
            f"{BASE_URL}/jobs/saved/{test_job_id}?email={test_user_email}"
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("is_saved") == False:
                print("✅ Job is correctly marked as unsaved")
            else:
                print("❌ Job should be unsaved but is still saved")
                return False
        else:
            print(f"❌ Check unsaved job failed: {response.text}")
            return False

        # 6. Verify saved jobs list is empty
        print("\n6. Verifying saved jobs list is empty...")
        response = requests.get(
            f"{BASE_URL}/jobs/saved?email={test_user_email}"
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            saved_jobs = response.json()
            if len(saved_jobs) == 0:
                print("✅ Saved jobs list is correctly empty")
            else:
                print(f"❌ Saved jobs list should be empty but has {len(saved_jobs)} items")
                return False
        else:
            print(f"❌ Get saved jobs after unsave failed: {response.text}")
            return False

        print("\n🎉 All Saved Jobs API tests passed!")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_saved_jobs_api()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
