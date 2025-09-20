import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv
load_dotenv()

import newspaper
from newspaper import Article
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import warnings
from newspaper import Config, ArticleException, ArticleBinaryDataException
import requests
import json
from openai import OpenAI # <-- MODIFIED: Import OpenAI

warnings.simplefilter(action="ignore", category=FutureWarning)

# --- Configure OpenAI API ---
try:
    # The OpenAI client will automatically look for the OPENAI_API_KEY
    # environment variable.
    client = OpenAI()
except Exception as e:
    print("="*50)
    print(">>> ERROR: Please set your OPENAI_API_KEY environment variable. <<<")
    print(f"Details: {e}")
    print("="*50)
    exit()

# --- Configure Newspaper ---
config = Config()
config.memoize_articles = False
config.request_timeout = 20

# --- OpenAI Summary Function (REPLACED) ---
def generate_summary(text, prompt_type="article"):
    """Generates a summary for a given text using the OpenAI API."""
    
    if not text or not isinstance(text, str) or len(text.strip()) < 100:
        return "Not enough content to summarize."

    system_prompt = ""
    user_prompt = ""

    if prompt_type == "article":
        system_prompt = "You are a helpful assistant that summarizes news articles concisely."
        user_prompt = f"Summarize the following news article in 2-3 concise sentences, focusing on the main points:\n\n---\n{text}\n---\n\nSummary:"
    else:  # for clusters
        system_prompt = "You are a helpful assistant that synthesizes information from multiple article summaries into a coherent overview."
        user_prompt = f"The following are summaries from multiple news articles covering the same event. Synthesize them into a single, comprehensive overview of 3-4 sentences. Identify the core event and any significant variations or agreements between the sources:\n\n---\n{text}\n---\n\nOverall Summary:"

    try:
        response = client.chat.completions.create(
            # Using a fast and cost-effective model
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5, # A bit of creativity but still factual
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred during OpenAI summary generation: {e}"


# ==============================================================================
# --- Data Collection (MODIFIED to use a fixed list of articles) ---
# ==============================================================================

test_articles = {
    "CNN": "https://www.cnn.com/2025/09/19/politics/trump-asks-supreme-court-to-let-him-deport-300-000-venezuelans",
    "Washington Post": "https://www.washingtonpost.com/politics/2025/09/19/trump-administration-noem-venezuela-tps-supreme-court/",
    "Guardian": "https://www.theguardian.com/us-news/2025/sep/19/trump-tps-immigration-venezuela",
    "PBS": "https://www.pbs.org/newshour/politics/doj-asks-supreme-court-to-strip-legal-protections-from-300000-venezuelan-migrants",
    "NYT": "https://www.nytimes.com/2025/09/19/us/trump-supreme-court-protections-venezuelans.html",
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
}
session = requests.Session()
session.headers.update(headers)

articles = []
article_info = []
article_details = {}

print("--- Starting Article Collection from Fixed List ---")

for source_name, url in test_articles.items():
    print(f"\nProcessing [{source_name}]: {url}")
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()

        art = Article(url, config=config, language='en')
        art.html = response.text
        art.parse()
        
        if len(art.text.strip()) > 100:
            print(f"  -> Summarizing '{art.title[:50]}...' with OpenAI")
            summary = generate_summary(art.text, prompt_type="article")
            
            identifier = (source_name, art.title, art.url)
            articles.append(art.text)
            article_info.append(identifier)
            article_details[identifier] = {
                "text": art.text,
                "summary": summary
            }
        else:
            print("  -> Skipped: Not enough text content found after parsing.")

    except requests.exceptions.RequestException as e:
        print(f"  -> Skipped due to download error: {e}")
    except Exception as e:
        print(f"  -> Skipped due to an unexpected error during parsing: {e}")

print(f"\n--- Total articles collected: {len(articles)} ---")


# ==============================================================================
# --- AI Processing & Clustering (No changes needed below this line) ---
# ==============================================================================

if not articles:
    print("\nNo articles were successfully collected. Exiting program.")
    exit()

print("\nEncoding articles...")
model = SentenceTransformer("all-MiniLM-L6-v2")
if len(articles) > 1:
    embeddings = model.encode(articles, convert_to_numpy=True)
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)

    print("Building FAISS index and finding similarities...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    sims, _ = index.search(embeddings, k=len(articles))

    clusters = []
    visited = set()
    for i in range(len(article_info)):
        if i in visited:
            continue
        
        similar_indices = np.where(sims[i] >= 0.70)[0]
        
        if len(similar_indices) > 1:
            cluster = []
            for j in similar_indices:
                if j not in visited:
                    cluster.append(article_info[j])
                    visited.add(j)
            if cluster:
                clusters.append(cluster)
else:
    clusters = []

print("\nBuilding final JSON structure...")
output_data = {}

for i, cluster in enumerate(clusters, 1):
    if len(cluster) > 1:
        cluster_key = f"Cluster {i}"
        
        cluster_summaries = [article_details[identifier]["summary"] for identifier in cluster]
        combined_summaries = "\n".join(f"- {s}" for s in cluster_summaries)
        cluster_overview = generate_summary(combined_summaries, prompt_type="cluster")

        articles_in_cluster = {}
        for identifier in cluster:
            title = identifier[1]
            details = article_details[identifier]
            
            articles_in_cluster[title] = {
                "text of article": details["text"],
                "summary of article": details["summary"]
            }
        
        output_data[cluster_key] = {
            "Summary of Clusters": cluster_overview,
            "Articles": articles_in_cluster
        }

file_path = 'clusters.json'
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

if not output_data:
    print(f"\nNo clusters were formed. A cluster requires at least 2 similar articles.")
else:
    print(f"\nSuccessfully wrote {len(output_data)} clusters to '{file_path}'")