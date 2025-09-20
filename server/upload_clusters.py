import json
import requests

# Configuration
API_BASE_URL = "http://localhost:5000"
JSON_FILE = "clusters.json"

def upload_clusters():
    """Upload clusters.json to database using Flask API endpoints."""
    
    # Load the clusters.json file
    print("Loading clusters.json...")
    with open(JSON_FILE, 'r') as f:
        clusters_data = json.load(f)
    
    print(f"Found {len(clusters_data)} clusters to upload")
    
    # Transform the data for the bulk upload endpoint
    clusters_list = []
    
    for cluster_id, cluster_info in clusters_data.items():
        cluster_entry = {
            "cluster": {
                "cluster_summary": cluster_info["cluster_summary"],
                "cluster_title": cluster_info["cluster_name"]  # Map cluster_name to cluster_title
            },
            "articles": cluster_info["articles"]  # Articles already have correct format
        }
        clusters_list.append(cluster_entry)
    
    # Prepare the payload for bulk upload
    payload = {
        "clusters": clusters_list
    }
    
    # Send to the bulk endpoint
    print(f"\nUploading {len(clusters_list)} clusters to database...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/data/bulk",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            summary = result.get("summary", {})
            
            print("\n✅ Upload successful!")
            print(f"   Clusters created: {summary.get('total_clusters_created', 0)}")
            print(f"   Articles created: {summary.get('total_articles_created', 0)}")
            
        else:
            print(f"\n❌ Upload failed with status {response.status_code}")
            error_msg = response.json().get("error", "Unknown error")
            print(f"   Error: {error_msg}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to Flask server!")
        print("   Make sure server.py is running: python server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    upload_clusters()