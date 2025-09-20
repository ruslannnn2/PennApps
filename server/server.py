from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
# allow cross-origin requests from the front-end dev server
CORS(app)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.route("/server", methods=["GET"])
def home():
    return "Hello, World!"


@app.route("/health", methods=["GET"])
def health():
    try:
        response = "hello"
        return jsonify({"status": "ok", "supabase_connected": True}), 200
    except Exception as e:
        return jsonify({"status": "error", "supabase_connected": False, "error": str(e)}), 500

@app.route("/api/clusters", methods=["GET"])
def get_all_clusters():
    try:
        result = supabase.table('clusters').select("*").execute()
        data = result.data or []
        return jsonify({
            "clusters": data,
            "total": len(data)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/clusters/<int:cluster_number>', methods=["GET"])
def get_cluster_by_number(cluster_number):
    try:
        result = supabase.table('clusters').select("*").eq('cluster_number', cluster_number).execute()
        if not result.data:
            return jsonify({"error": "Cluster not found"}), 404
        return jsonify({"cluster": result.data[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles', methods=["GET"])
def get_all_articles():
    try:
        result = supabase.table('articles').select("*").execute()
        data = result.data or []
        return jsonify({
            "articles": data,
            "total": len(data)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/clusters/<int:cluster_number>/articles', methods=["GET"])
def get_articles_by_cluster(cluster_number):
    try:
        cluster_result = supabase.table('clusters').select("*").eq('cluster_number', cluster_number).execute()
        if not cluster_result.data:
            return jsonify({"error": "Cluster not found"}), 404

        cluster = cluster_result.data[0]

        articles_result = supabase.table('articles').select("*").eq('cluster_id', cluster['id']).execute()
        articles = articles_result.data or []

        return jsonify({
            "cluster_number": cluster_number,
            "cluster_summary": cluster.get('cluster_summary'),
            "articles": articles,
            "article_count": len(articles)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=["GET"])
def get_article_by_id(article_id):
    try:
        result = supabase.table('articles').select(
            "*, clusters(cluster_number, cluster_summary)"
        ).eq('id', article_id).execute()
        if not result.data:
            return jsonify({"error": "Article not found"}), 404

        return jsonify({
            "article": result.data[0]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)