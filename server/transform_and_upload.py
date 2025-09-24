import json
import requests
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:5000"

def transform_raw_data(raw_data):
    transformed_clusters = []
    
    for cluster_id, cluster_data in raw_data.items():
        # Transform cluster data
        cluster_info = {
            "cluster": {
                "cluster_summary": cluster_data["cluster_summary"],
                "cluster_title": cluster_data["cluster_name"]  # Using cluster_name as title
            },
            "articles": []
        }
        
        # Transform articles data
        for article in cluster_data["articles"]:
            article_data = {
                "title": article["title"],
                "text": article["text"],
                "article_summary": article["article_summary"],
                "source": article["source"]
            }
            cluster_info["articles"].append(article_data)
        
        transformed_clusters.append(cluster_info)
    
    return transformed_clusters

def upload_single_cluster(cluster_data):
    """
    Upload a single cluster with its articles using the batch endpoint.
    
    Args:
        cluster_data: Dictionary containing cluster and articles data
        
    Returns:
        Response from the API
    """
    endpoint = f"{API_BASE_URL}/api/clusters/batch"
    
    try:
        response = requests.post(
            endpoint,
            json=cluster_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading cluster: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        raise

def upload_all_clusters_bulk(clusters_data):
    """
    Upload all clusters at once using the bulk endpoint.
    
    Args:
        clusters_data: List of cluster dictionaries
        
    Returns:
        Response from the API
    """
    endpoint = f"{API_BASE_URL}/api/data/bulk"
    
    payload = {
        "clusters": clusters_data
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading clusters in bulk: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        raise

def check_server_health():
    """
    Check if the server is running and accessible.
    
    Returns:
        True if server is healthy, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    """
    Main function to execute the data transformation and upload process.
    """
    # Check server health first
    print("Checking server health...")
    if not check_server_health():
        print("Server is not accessible. Please ensure the Flask server is running.")
        print(f"   Server URL: {API_BASE_URL}")
        return
    
    print("Server is healthy\n")
    
    # Load the raw data from file
    print("Loading raw data from file...")
    try:
        with open('rawdata.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        print(f"Loaded data for {len(raw_data)} clusters\n")
    except FileNotFoundError:
        print("rawdata.json file not found. Please ensure the file exists in the current directory.")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return
    
    # Transform the data
    print("Transforming data...")
    transformed_clusters = transform_raw_data(raw_data)
    print(f"Transformed {len(transformed_clusters)} clusters\n")
    
    # Calculate total articles
    total_articles = sum(len(cluster['articles']) for cluster in transformed_clusters)
    print(f"Total articles to upload: {total_articles}\n")
    
    # Ask user for upload method
    print("Choose upload method:")
    print("1. Upload all clusters at once (bulk upload)")
    print("2. Upload clusters one by one")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        # Bulk upload
        print("\nStarting bulk upload...")
        try:
            result = upload_all_clusters_bulk(transformed_clusters)
            
            if result.get('success'):
                print(f"\nBulk upload successful!")
                print(f"   - Clusters created: {result['summary']['total_clusters_created']}")
                print(f"   - Articles created: {result['summary']['total_articles_created']}")
                print(f"   - Message: {result['message']}")
            else:
                print(f"\nBulk upload failed: {result.get('error')}")
                
        except Exception as e:
            print(f"\nError during bulk upload: {e}")
            
    elif choice == '2':
        # Individual upload
        print("\nStarting individual uploads...")
        successful_uploads = 0
        failed_uploads = 0
        
        for i, cluster_data in enumerate(transformed_clusters, 1):
            cluster_title = cluster_data['cluster'].get('cluster_title', f'Cluster {i}')
            print(f"\nUploading cluster {i}/{len(transformed_clusters)}: {cluster_title}")
            print(f"  Articles: {len(cluster_data['articles'])}")
            
            try:
                result = upload_single_cluster(cluster_data)
                
                if result.get('success'):
                    successful_uploads += 1
                    print(f"Success! Cluster ID: {result['cluster']['cluster_id']}")
                else:
                    failed_uploads += 1
                    print(f"Failed: {result.get('error')}")
                    
            except Exception as e:
                failed_uploads += 1
                print(f"Error: {e}")
        
        # Print summary
        print(f"\n{'='*50}")
        print("Upload Summary:")
        print(f"Successful: {successful_uploads}/{len(transformed_clusters)}")
        print(f"Failed: {failed_uploads}/{len(transformed_clusters)}")
        
    else:
        print("\nInvalid choice. Please run the script again and choose 1 or 2.")
        return
    
    print("\nProcess completed!")

if __name__ == "__main__":
    main()