#!/usr/bin/env python3
"""
Test script to verify the health endpoints work correctly
"""

import requests
import json
import sys

def test_endpoint(url, endpoint):
    """Test a specific endpoint"""
    try:
        full_url = f"{url}{endpoint}"
        print(f"🔍 Testing: {full_url}")
        
        response = requests.get(full_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}...")
            print("   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    """Test the health endpoints"""
    print("🚀 Testing Orizon Google Maps Scraper Health Endpoints")
    print("=" * 60)
    
    # Test locally first
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/",
        "/test",
        "/health"
    ]
    
    results = []
    for endpoint in endpoints:
        success = test_endpoint(base_url, endpoint)
        results.append(success)
        print()
    
    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} endpoints working")
    
    if all(results):
        print("✅ All endpoints are working correctly!")
        return 0
    else:
        print("❌ Some endpoints failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
