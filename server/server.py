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
    
@app.route('/api/clusters/<int:cluster_id>/articles', methods=["GET"])
def get_articles_by_cluster(cluster_id):
    try:
        cluster_result = supabase.table('clusters').select("*").eq('cluster_id', cluster_id).execute()
        if not cluster_result.data:
            return jsonify({"error": "Cluster not found"}), 404

        cluster = cluster_result.data[0]

        articles_result = supabase.table('articles').select("*").eq('cluster_id', cluster_id).execute()
        articles = articles_result.data or []

        return jsonify({
            "cluster_id": cluster_id,
            "cluster_summary": cluster.get('cluster_summary'),
            "articles": articles,
            "article_count": len(articles)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/clusters/<int:cluster_id>', methods=["GET"])
def get_cluster_by_id(cluster_id):
    try:
        result = supabase.table('clusters').select("cluster_id, cluster_summary").eq('cluster_id', cluster_id).execute()
        if not result.data:
            return jsonify({"error": "Cluster not found"}), 404
        
        cluster = result.data[0]
        return jsonify({
            "cluster_id": cluster.get("cluster_id"),
            "cluster_title": cluster.get("cluster_summary")
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=["GET"])
def get_article_by_id(article_id):
    try:
        result = supabase.table('articles').select("*").eq('article_id', article_id).execute()
        if not result.data:
            return jsonify({"error": "Article not found"}), 404

        return jsonify({
            "article": result.data[0]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clusters/batch', methods=["POST"])
def create_cluster_with_articles():
    """
    Create a cluster and all its articles in one request
    Expected format:
    {
        "cluster": {
            "cluster_id": 1,
            "cluster_summary": "Technology news cluster",
            "cluster_title": "Tech News"
        },
        "articles": [
            {
                "article_id": 1,
                "title": "Article 1",
                "text": "Content...",
                "article_summary": "Summary...",
                "source": "Source 1"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        cluster_data = data.get('cluster')
        articles_data = data.get('articles', [])
        
        if not cluster_data:
            return jsonify({"error": "Cluster data is required"}), 400
        
        if not cluster_data.get('cluster_summary'):
            return jsonify({"error": "cluster_summary is required"}), 400
        
        # Step 1: Create the cluster
        cluster_insert_data = {
            'cluster_summary': cluster_data.get('cluster_summary')
        }
        
        # Include cluster_id if provided
        if cluster_data.get('cluster_id'):
            cluster_insert_data['cluster_id'] = cluster_data.get('cluster_id')
        
        # Include cluster_title if provided
        if cluster_data.get('cluster_title'):
            cluster_insert_data['cluster_title'] = cluster_data.get('cluster_title')
        
        cluster_result = supabase.table('clusters').insert(cluster_insert_data).execute()
        
        if not cluster_result.data:
            return jsonify({
                "success": False,
                "error": "Failed to create cluster"
            }), 500
        
        created_cluster = cluster_result.data[0]
        cluster_id = created_cluster.get('cluster_id')
        
        # Step 2: Create all articles for this cluster
        created_articles = []
        if articles_data:
            # Validate articles
            for i, article in enumerate(articles_data):
                if not article.get('title') or not article.get('text'):
                    return jsonify({
                        "error": f"Article {i+1} missing required fields (title, text)"
                    }), 400
            
            # Prepare articles with cluster_id
            articles_insert_data = []
            for article in articles_data:
                article_data = {
                    'cluster_id': cluster_id,
                    'title': article.get('title'),
                    'text': article.get('text'),
                    'article_summary': article.get('article_summary'),
                    'source': article.get('source')
                }
                
                # Include article_id if provided
                if article.get('article_id'):
                    article_data['article_id'] = article.get('article_id')
                
                # Remove None values
                article_data = {k: v for k, v in article_data.items() if v is not None}
                articles_insert_data.append(article_data)
            
            # Bulk insert articles
            articles_result = supabase.table('articles').insert(articles_insert_data).execute()
            
            if articles_result.data:
                created_articles = articles_result.data
            else:
                # If articles failed, we might want to clean up the cluster
                return jsonify({
                    "success": False,
                    "error": "Cluster created but failed to create articles",
                    "cluster": created_cluster
                }), 500
        
        return jsonify({
            "success": True,
            "cluster": created_cluster,
            "articles": created_articles,
            "summary": {
                "cluster_id": cluster_id,
                "articles_created": len(created_articles),
                "total_items": 1 + len(created_articles)
            },
            "message": f"Successfully created cluster {cluster_id} with {len(created_articles)} articles"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/data/bulk', methods=["POST"])
def create_multiple_clusters_with_articles():
    """
    Create multiple clusters, each with their sorted articles
    Expected format:
    {
        "clusters": [
            {
                "cluster": {
                    "cluster_id": 1,
                    "cluster_summary": "Tech cluster",
                    "cluster_title": "Technology"
                },
                "articles": [
                    {
                        "article_id": 1,
                        "title": "Article 1",
                        "text": "Content...",
                        "article_summary": "Summary...",
                        "source": "Source 1"
                    }
                ]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'clusters' not in data:
            return jsonify({"error": "No clusters data provided"}), 400
        
        clusters_data = data.get('clusters', [])
        
        if not clusters_data:
            return jsonify({"error": "Clusters array is empty"}), 400
        
        results = []
        total_clusters_created = 0
        total_articles_created = 0
        
        for i, cluster_batch in enumerate(clusters_data):
            try:
                cluster_info = cluster_batch.get('cluster')
                articles_info = cluster_batch.get('articles', [])
                
                if not cluster_info or not cluster_info.get('cluster_summary'):
                    return jsonify({
                        "error": f"Cluster {i+1} missing required cluster data"
                    }), 400
                
                # Create cluster
                cluster_insert_data = {
                    'cluster_summary': cluster_info.get('cluster_summary')
                }
                
                if cluster_info.get('cluster_id'):
                    cluster_insert_data['cluster_id'] = cluster_info.get('cluster_id')
                
                if cluster_info.get('cluster_title'):
                    cluster_insert_data['cluster_title'] = cluster_info.get('cluster_title')
                
                cluster_result = supabase.table('clusters').insert(cluster_insert_data).execute()
                
                if not cluster_result.data:
                    return jsonify({
                        "success": False,
                        "error": f"Failed to create cluster {i+1}",
                        "partial_results": results
                    }), 500
                
                created_cluster = cluster_result.data[0]
                cluster_id = created_cluster.get('cluster_id')
                total_clusters_created += 1
                
                # Create articles for this cluster
                created_articles = []
                if articles_info:
                    # Validate articles
                    for j, article in enumerate(articles_info):
                        if not article.get('title') or not article.get('text'):
                            return jsonify({
                                "error": f"Cluster {i+1}, Article {j+1} missing required fields"
                            }), 400
                    
                    # Prepare articles
                    articles_insert_data = []
                    for article in articles_info:
                        article_data = {
                            'cluster_id': cluster_id,
                            'title': article.get('title'),
                            'text': article.get('text'),
                            'article_summary': article.get('article_summary'),
                            'source': article.get('source')
                        }
                        
                        # Include article_id if provided
                        if article.get('article_id'):
                            article_data['article_id'] = article.get('article_id')
                        
                        article_data = {k: v for k, v in article_data.items() if v is not None}
                        articles_insert_data.append(article_data)
                    
                    # Insert articles
                    articles_result = supabase.table('articles').insert(articles_insert_data).execute()
                    
                    if articles_result.data:
                        created_articles = articles_result.data
                        total_articles_created += len(created_articles)
                
                results.append({
                    "cluster": created_cluster,
                    "articles": created_articles,
                    "articles_count": len(created_articles)
                })
                
            except Exception as cluster_error:
                return jsonify({
                    "success": False,
                    "error": f"Error processing cluster {i+1}: {str(cluster_error)}",
                    "partial_results": results
                }), 500
        
        return jsonify({
            "success": True,
            "results": results,
            "summary": {
                "total_clusters_created": total_clusters_created,
                "total_articles_created": total_articles_created,
                "total_batches_processed": len(results)
            },
            "message": f"Successfully created {total_clusters_created} clusters with {total_articles_created} articles"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/clusters/<int:cluster_id>/articles/batch', methods=["POST"])
def add_articles_to_existing_cluster(cluster_id):
    """
    Add multiple articles to an existing cluster
    Expected format:
    {
        "articles": [
            {
                "article_id": 10,
                "title": "New Article 1",
                "text": "Content...",
                "article_summary": "Summary...",
                "source": "Source"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'articles' not in data:
            return jsonify({"error": "No articles data provided"}), 400
        
        articles_data = data.get('articles', [])
        
        if not articles_data:
            return jsonify({"error": "Articles array is empty"}), 400
        
        # Check if cluster exists
        cluster_check = supabase.table('clusters').select("cluster_id").eq('cluster_id', cluster_id).execute()
        if not cluster_check.data:
            return jsonify({"error": "Cluster not found"}), 404
        
        # Validate articles
        for i, article in enumerate(articles_data):
            if not article.get('title') or not article.get('text'):
                return jsonify({
                    "error": f"Article {i+1} missing required fields (title, text)"
                }), 400
        
        # Prepare articles data
        articles_insert_data = []
        for article in articles_data:
            article_data = {
                'cluster_id': cluster_id,
                'title': article.get('title'),
                'text': article.get('text'),
                'article_summary': article.get('article_summary'),
                'source': article.get('source')
            }
            
            # Include article_id if provided
            if article.get('article_id'):
                article_data['article_id'] = article.get('article_id')
            
            article_data = {k: v for k, v in article_data.items() if v is not None}
            articles_insert_data.append(article_data)
        
        # Insert articles
        result = supabase.table('articles').insert(articles_insert_data).execute()
        
        if result.data:
            return jsonify({
                "success": True,
                "articles": result.data,
                "cluster_id": cluster_id,
                "articles_added": len(result.data),
                "message": f"Successfully added {len(result.data)} articles to cluster {cluster_id}"
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to add articles to cluster"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)