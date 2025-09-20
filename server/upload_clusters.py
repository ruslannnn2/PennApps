import json
import requests

# Configuration
API_BASE_URL = "http://localhost:5000"
CLUSTERS_FILE = "clusters.json"
ARTICLES_FILE = "articles.json"

def upload_data():
    """Upload clusters.json and articles.json to database using Flask API endpoints."""
    
    # Load the clusters.json file
    print(f"Loading {CLUSTERS_FILE}...")
    with open(CLUSTERS_FILE, 'r') as f:
        clusters_data = json.load(f)
    
    # Load the articles.json file
    print(f"Loading {ARTICLES_FILE}...")
    with open(ARTICLES_FILE, 'r') as f:
        articles_data = json.load(f)
    
    print(f"Found {len(clusters_data)} clusters")
    print(f"Found {len(articles_data)} article groups")
    
    # Prepare the data for the bulk upload endpoint
    clusters_list = []
    
    # Process clusters and match with their articles
    for cluster_id, cluster_info in clusters_data.items():
        # Get the corresponding articles for this cluster
        cluster_articles = articles_data.get(cluster_id, {}).get("articles", [])
        
        cluster_entry = {
            "cluster": {
                "cluster_summary": cluster_info.get("cluster_summary", ""),
                "cluster_title": cluster_info.get("cluster_title", "")
            },
            "articles": cluster_articles
        }
        clusters_list.append(cluster_entry)
    
    # Prepare the payload for bulk upload
    payload = {
        "clusters": clusters_list
    }
    
    # Send to the bulk endpoint
    print(f"\nUploading {len(clusters_list)} clusters with their articles to database...")
    
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
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            print(f"   Error: {error_msg}")
            
            # Check for partial results
            partial = error_data.get("partial_results", [])
            if partial:
                print(f"   Partial success: {len(partial)} clusters uploaded before failure")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to Flask server!")
        print("   Make sure server.py is running: python server.py")
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("   Make sure both clusters.json and articles.json exist")
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON format: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    upload_data()