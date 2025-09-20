# test_queries.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def test_clusters():
    print("🧪 Testing clusters table...")
    try:
        result = supabase.table('clusters').select("*").execute()
        print(f"✅ Found {len(result.data)} clusters")
        
        # Print first cluster as sample
        if result.data:
            print(f"Sample cluster: {result.data[0]['cluster_number']} - {result.data[0]['cluster_summary'][:50]}...")
    except Exception as e:
        print(f"❌ Clusters test failed: {e}")

def test_articles():
    print("\n🧪 Testing articles table...")
    try:
        result = supabase.table('articles').select("*").execute()
        print(f"✅ Found {len(result.data)} articles")
        
        # Print first article as sample
        if result.data:
            print(f"Sample article: {result.data[0]['title'][:50]}...")
    except Exception as e:
        print(f"❌ Articles test failed: {e}")

def test_join():
    print("\n🧪 Testing join query...")
    try:
        result = supabase.table('articles').select(
            "id, title, clusters(cluster_number)"
        ).execute()
        print(f"✅ Join successful! Found {len(result.data)} articles with cluster info")
        
        # Print sample
        if result.data:
            sample = result.data[0]
            print(f"Sample: Article '{sample['title'][:30]}...' in Cluster {sample['clusters']['cluster_number']}")
    except Exception as e:
        print(f"❌ Join test failed: {e}")

if __name__ == "__main__":
    test_clusters()
    test_articles()
    test_join()