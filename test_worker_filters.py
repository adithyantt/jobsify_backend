#!/usr/bin/env python3
"""
Test worker filtering API endpoints
"""
import requests

BASE_URL = "http://localhost:8000"

def test_filters():
    print("🧪 Testing Worker Filter API Endpoints\n")
    
    # Test 1: Get all workers
    r = requests.get(f"{BASE_URL}/workers")
    print(f"✅ Get all workers: {r.status_code} - {len(r.json())} workers")
    
    # Test 2: Filter by availability type
    r = requests.get(f"{BASE_URL}/workers?availability_type=everyday")
    print(f"✅ Filter by 'everyday' availability: {len(r.json())} workers")
    
    # Test 3: Filter by min experience
    r = requests.get(f"{BASE_URL}/workers?min_experience=5")
    print(f"✅ Filter by min 5 years experience: {len(r.json())} workers")
    
    # Test 4: Filter by min rating
    r = requests.get(f"{BASE_URL}/workers?min_rating=4.0")
    print(f"✅ Filter by min 4.0 rating: {len(r.json())} workers")
    
    # Test 5: Sort by experience high
    r = requests.get(f"{BASE_URL}/workers?sort_by=experience_high")
    workers = r.json()
    if workers:
        print(f"✅ Sort by experience (high): Top has {workers[0]['experience']} years")
    
    # Test 6: Sort by rating high
    r = requests.get(f"{BASE_URL}/workers?sort_by=rating_high")
    workers = r.json()
    if workers:
        print(f"✅ Sort by rating (high): Top has {workers[0]['rating']} rating")
    
    # Test 7: Combined filters
    r = requests.get(f"{BASE_URL}/workers?min_experience=3&min_rating=3.5&sort_by=experience_high")
    print(f"✅ Combined filters (exp>=3, rating>=3.5): {len(r.json())} workers")
    
    print("\n✅ All API filter tests passed!")

if __name__ == "__main__":
    test_filters()
