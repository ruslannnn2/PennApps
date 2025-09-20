import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, description):
    """Simple test function"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS")
            try:
                data = response.json()
                print("Response:", json.dumps(data, indent=2))
            except:
                print("Response:", response.text)
        else:
            print("❌ FAIL")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Simple tests
print("🚀 Testing Flask API")

test_endpoint("/server", "Home endpoint")
test_endpoint("/health", "Health check")
test_endpoint("/api/clusters", "Get all clusters")
test_endpoint("/api/articles", "Get all articles")
test_endpoint("/api/clusters/1", "Get cluster 1")
test_endpoint("/api/articles/1", "Get article 1")
test_endpoint("/api/clusters/1/articles", "Get cluster 1 articles")

print("\n🏁 Done!")