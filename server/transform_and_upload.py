import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

RAW_FILE = "rawdata.json"

"""
# Delete all existing clusters
delete_clusters = supabase.table("clusters").delete().neq("cluster_id", 0).execute()
deleted_clusters_count = len(delete_clusters.data) if delete_clusters.data else 0
print(f"Deleted {deleted_clusters_count} clusters")

# Delete all existing articles
delete_articles = supabase.table("articles").delete().neq("cluster_id", 0).execute()
deleted_articles_count = len(delete_articles.data) if delete_articles.data else 0
print(f"Deleted {deleted_articles_count} articles")
"""

def upload_data():
    print(f"Loading {RAW_FILE}...")
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    total_clusters = 0
    total_articles = 0

    for cluster_id_str, cluster_info in raw_data.items():
        cluster_id = int(cluster_id_str)
        cluster_title = cluster_info.get("cluster_name", "").strip('"')
        cluster_payload = {
            "cluster_id": cluster_id,
            "cluster_title": cluster_title,
            "cluster_summary": cluster_info.get("cluster_summary", "")
        }

        # Insert cluster
        cluster_res = supabase.table("clusters").insert(cluster_payload).execute()
        if cluster_res.status_code == 201:
            total_clusters += 1
        else:
            print(f"Failed to insert cluster {cluster_id}: {cluster_res.data}")

        # Insert articles
        articles_payload = [
            {
                "cluster_id": cluster_id,
                "title": art.get("title", ""),
                "text": art.get("text", ""),
                "article_summary": art.get("article_summary", ""),
                "source": art.get("source", "")
            }
            for art in cluster_info.get("articles", [])
        ]

        if articles_payload:
            articles_res = supabase.table("articles").insert(articles_payload).execute()
            if articles_res.status_code == 201:
                total_articles += len(articles_payload)
            else:
                print(f"Failed to insert articles for cluster {cluster_id}: {articles_res.data}")

        print(f"Cluster {cluster_id}: {len(articles_payload)} articles uploaded")

    print("\nUpload complete!")
    print(f"Total clusters uploaded: {total_clusters}")
    print(f"Total articles uploaded: {total_articles}")


if __name__ == "__main__":
    upload_data()
