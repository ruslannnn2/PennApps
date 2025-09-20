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
import google.generativeai as genai 
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))



warnings.simplefilter(action="ignore", category=FutureWarning)

# NEW: Configure the Gemini API with your key
try:
    # Replace with your actual API key
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except AttributeError:
    print("="*50)
    print(">>> ERROR: Please set your GEMINI_API_KEY environment variable. <<<")
    print("="*50)
    exit()

config = Config()
config.memoize_articles = False
config.browser_user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0 Safari/537.36"
)


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



# --- Build newspapers ---
sources = {
    "CNN": "https://www.cnn.com",
    "Guardian": "https://www.theguardian.com",
    "NYT": "https://www.nytimes.com",
    "NY Post": "https://nypost.com"
}

# Limit number of articles per source for demo / speed
MAX_ARTICLES = 2000

# Fetch articles from each newspaper
articles = []
article_info = []  # store (source, title, url) for each article
article_details = {} # NEW: maps identifier tuple to its text and summary


for source_name, url in sources.items():
    print(f"\nBuilding {source_name}…")
    try:
        # Use requests to fetch the homepage (with UA)
        resp = requests.get(
            url,
            headers={"User-Agent": config.browser_user_agent},
            timeout=30,
        )
        resp.raise_for_status()

        paper = newspaper.build(
            url,
            config=config,
            memoize_articles=False,
            input_html=resp.text,  # pass HTML we just fetched
        )
    except Exception as e:
        print(f"  [!] Could not build {source_name}: {e}")
        continue

    count = 0
    for art in paper.articles:
        if count >= MAX_ARTICLES:
            break
        try:
            art.download()
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
            count+=1

        except (ArticleException, ArticleBinaryDataException):
            continue
        except Exception as e:
            print(f"  Skipped article: {e}")
            continue

    print(f"  Collected {count} good articles from {source_name}")

print(f"\nTotal articles collected: {len(articles)}")


# --- Encode & normalize ---
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = []
for text in articles:
    vec = model.encode(text, convert_to_numpy=True)
    embeddings.append(vec)

embeddings = np.stack(embeddings)
embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)

# --- Build FAISS index ---
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

# --- Cross similarity matrix ---
sims, idxs = index.search(embeddings, k=len(articles))  # each article vs all others

# --- Create dictionary of similarities ---
similarity_dict = {}
for i, info_i in enumerate(article_info):
    similarity_dict[info_i] = []
    for j, info_j in enumerate(article_info):
        if i != j and sims[i, j] >= 0.70:  # threshold for clustering
            similarity_dict[info_i].append((info_j, sims[i, j]))

# --- Cluster articles based on similarity >= 0.75 ---
clusters = []
visited = set()

for idx, key in enumerate(article_info):
    if key in visited:
        continue
    cluster = [key]
    visited.add(key)
    to_check = [key]
    while to_check:
        current = to_check.pop()
        for neighbor, score in similarity_dict.get(current, []):
            if neighbor not in visited:
                cluster.append(neighbor)
                visited.add(neighbor)
                to_check.append(neighbor)
    clusters.append(cluster)

# --- Generate JSON Output ---
print("\nBuilding final JSON structure...")
output_data = {}

for i, cluster in enumerate(clusters, 1):
    # We'll only output actual clusters (more than 1 article)
    if len(cluster) > 1:
        cluster_key = f"Cluster {i}"
        
        # --- 1. Generate the cluster-level summary ---
        cluster_summaries = [article_details[identifier]["summary"] for identifier in cluster]
        combined_summaries = "\n".join(f"- {s}" for s in cluster_summaries)
        cluster_overview = generate_summary(combined_summaries, prompt_type="cluster")

        # --- 2. Build the dictionary of articles for this cluster ---
        articles_in_cluster = {}
        for identifier in cluster:
            # identifier is a tuple: (source, title, url)
            title = identifier[1]
            details = article_details[identifier]
            
            articles_in_cluster[title] = {
                "text of article": details["text"],
                "summary of article": details["summary"]
            }
        
        # --- 3. Add the complete cluster data to our main dictionary ---
        output_data[cluster_key] = {
            "Summary of Clusters": cluster_overview,
            "Articles": articles_in_cluster
        }

# --- 4. Write the dictionary to a JSON file ---
file_path = 'clusters.json'
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"\nSuccessfully wrote {len(output_data)} clusters to '{file_path}'")









