from flask import Flask, jsonify
from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/api/server", methods=["GET"])
def home():
    return "Hello, World!"


@app.route("/api/health", methods=["GET"])
def health():
    try:
        response = "hello"
        return jsonify({"status": "ok", "supabase_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "error", "supabase_connected": False, "error": str(e)}), 500

@app.route("/api/clusters", methods="GET")
def getAllClusters():
    try:
        result = supabase.table('clusters').select("*").execute()
        
        return jsonify({
            "clusters": result.data,
            "total": len(result.data)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles', methods=['GET'])
def get_all_articles():
    try:
        result = supabase.table('articles').select("*").execute()
        
        return jsonify({
            "articles": result.data,
            "total": len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/clusters/<int:cluster_number>/articles', methods=['GET'])
def get_articles_by_cluster(cluster_number):
    
    try:
        cluster_result = supabase.table('clusters').select("*").eq('cluster_number', cluster_number).execute()
        
        if not cluster_result.data:
            return jsonify({"error": "Cluster not found"}), 404
        
        cluster = cluster_result.data[0]
        
        articles_result = supabase.table('articles').select("*").eq('cluster_id', cluster['id']).execute()
        
        return jsonify({
            "cluster_number": cluster_number,
            "cluster_summary": cluster['cluster_summary'],
            "articles": articles_result.data,
            "article_count": len(articles_result.data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)