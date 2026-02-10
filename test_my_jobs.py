import requests

def test_my_jobs():
    # Test the my jobs endpoint
    base_url = "http://10.13.1.95:38010"  # Updated to match the error log
    email = "vivekkrishna960@gmail.com"  # Use the email from the error

    try:
        response = requests.get(f"{base_url}/jobs/my?email={email}", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Jobs retrieved:")
            jobs = response.json()
            print(f"Number of jobs: {len(jobs)}")
            for job in jobs:
                print(f"ID: {job['id']}, Title: {job['title']}, Created At: {job['created_at']}")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_my_jobs()
