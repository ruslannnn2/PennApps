import json

def split_clusters_and_articles(input_file, clusters_output, articles_output):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    clusters = []
    articles = []

    # If the JSON is a dict, convert to list of (id, data)
    if isinstance(data, dict):
        iterable = data.items()
    elif isinstance(data, list):
        # List of clusters (no explicit IDs)
        iterable = enumerate(data, start=1)
    else:
        raise ValueError("Unexpected JSON format")

    for cluster_id, cluster_data in iterable:
        cluster_obj = {
            "cluster_id": str(cluster_id),
            "cluster_title": cluster_data.get("cluster_name"),
            "cluster_summary": cluster_data.get("cluster_summary")
        }
        clusters.append(cluster_obj)

        # Create article objects, each tied to cluster_id
        for article in cluster_data.get("articles", []):
            article_obj = {"cluster_id": cluster_id, **article}
            articles.append(article_obj)

    with open(clusters_output, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=4, ensure_ascii=False)

    with open(articles_output, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    split_clusters_and_articles(
        input_file="rawdata.json",
        clusters_output="clusters.json",
        articles_output="articles.json"
    )
