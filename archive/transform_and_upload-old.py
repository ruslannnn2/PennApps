import json
import requests
from collections import defaultdict

# Configuration
API_BASE_URL = "http://localhost:5000"
CLUSTERS_FILE = "clusters.json"
ARTICLES_FILE = "articles.json"

def upload_data():
    """Upload clusters.json and articles.json to database using Flask API endpoints."""
    
    # Load the clusters.json file
    print(f"Loading {CLUSTERS_FILE}...")
    with open(CLUSTERS_FILE, 'r', encoding='utf-8') as f:
        clusters_data = json.load(f)
    
    # Load the articles.json file
    print(f"Loading {ARTICLES_FILE}...")
    with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    print(f"Found {len(clusters_data)} clusters")
    print(f"Found {len(articles_data)} articles")
    
    # Group articles by cluster_id
    articles_by_cluster = defaultdict(list)
    for article in articles_data:
        cluster_id = article["cluster_id"]
        articles_by_cluster[cluster_id].append({
            "title": article["title"],
            "text": article["text"],
            "article_summary": article["article_summary"],
            "source": article["source"]
        })
    
    # Prepare the data for the bulk upload endpoint
    clusters_list = []
    
    # Process each cluster
    for cluster in clusters_data:
        cluster_id = cluster["cluster_id"]
        
        # Get the articles for this cluster
        cluster_articles = articles_by_cluster.get(cluster_id, [])
        
        cluster_entry = {
            "cluster": {
                "cluster_id": int(cluster_id),  # Convert string to int
                "cluster_summary": cluster["cluster_summary"],
                "cluster_title": cluster["cluster_title"]
            },
            "articles": cluster_articles
        }
        clusters_list.append(cluster_entry)
        
        print(f"  Cluster {cluster_id}: {len(cluster_articles)} articles")
    
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
            
            print("\nUpload successful!")
            print(f"   Total clusters created: {summary.get('total_clusters_created', 0)}")
            print(f"   Total articles created: {summary.get('total_articles_created', 0)}")
            
            # Show details for each cluster
            results = result.get("results", [])
            if results:
                print("\nCluster details:")
                for r in results:
                    cluster_info = r.get("cluster", {})
                    print(f"   - Cluster {cluster_info.get('cluster_id')}: {r.get('articles_count', 0)} articles uploaded")
            
        else:
            print(f"\nUpload failed with status {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get("error", "Unknown error")
                print(f"   Error: {error_msg}")
                
                # Check for partial results
                partial = error_data.get("partial_results", [])
                if partial:
                    print(f"   Partial success: {len(partial)} clusters uploaded before failure")
            except:
                print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\nCannot connect to Flask server!")
        print("   Make sure server.py is running: python server.py")
    except FileNotFoundError as e:
        print(f"\nFile not found: {e}")
        print("   Make sure both clusters.json and articles.json exist in the current directory")
    except json.JSONDecodeError as e:
        print(f"\nInvalid JSON format: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload_data()