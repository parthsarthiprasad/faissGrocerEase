#!/usr/bin/env python3
import requests
import json

def test_search_service():
    base_url = "http://localhost:8000"
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        print(f"Basic connectivity: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Basic connectivity failed: {e}")
        return False
    
    # Test search endpoint
    try:
        search_data = {
            "query": "milk",
            "lat": 40.7128,
            "lon": -74.0060,
            "radius_km": 5,
            "max_results": 5
        }
        
        response = requests.post(
            f"{base_url}/search/",
            headers={"Content-Type": "application/json"},
            json=search_data
        )
        
        print(f"Search endpoint: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} results")
            if results:
                print(f"First result: {results[0]}")
        else:
            print(f"Search failed: {response.text}")
            
    except Exception as e:
        print(f"Search test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing GrocerEase Search Service...")
    success = test_search_service()
    if success:
        print("✅ Search service is working!")
    else:
        print("❌ Search service has issues") 