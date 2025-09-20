import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv
load_dotenv()

import feedparser
import newspaper
from newspaper import Article, Config, ArticleException, ArticleBinaryDataException
import faiss
import numpy as np
import warnings
import requests
import google.generativeai as genai
import json
from openai import OpenAI
from datetime import datetime, timedelta, timezone

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

warnings.simplefilter(action="ignore", category=FutureWarning)

# --- Gemini key check ---
try:
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


#  RSS integration part  


### NEW: constants and helper
CUTOFF = datetime.now(timezone.utc) - timedelta(hours=72)
RSS_FEEDS = {
    "CNN": "http://rss.cnn.com/rss/cnn_latest.rss",
    "Guardian": "https://www.theguardian.com/world/rss",
    "NYPost": "https://nypost.com/feed/",
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Politico": "https://rss.politico.com/politics-news.xml",
    "Politico - Congress": "https://rss.politico.com/congress.xml",
    "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Fox": "https://feeds.foxnews.com/foxnews/latest"
}


def collect_from_rss(src, url):
    feed = feedparser.parse(url)
    results = []
    for e in feed.entries:
        pub = e.get("published_parsed") or e.get("updated_parsed")
        if not pub:
            continue
        if datetime(*pub[:6], tzinfo=timezone.utc) < CUTOFF:
            continue
        try:
            art = Article(e.link, config=config)
            art.download()
            art.parse()
            if len(art.text.strip()) >= 120:
                results.append((src, art.title, e.link, art.text))
        except (ArticleException, Exception):
            continue
    return results


# --- OpenAI Summary ---
def generate_summary(text, prompt_type="article"):
    if not text or not isinstance(text, str) or len(text.strip()) < 100:
        return "Not enough content to summarize."

    if prompt_type == "article":
        system_prompt = "You are a helpful assistant that summarizes news articles concisely."
        user_prompt = (
            f"Summarize the following news article in 2-3 concise sentences, focusing on the main points:\n\n---\n{text}\n---\n\nSummary:"
        )
    else:
        system_prompt = "You are a helpful assistant that synthesizes information from multiple article summaries into a coherent overview."
        user_prompt = (
            f"The following are summaries from multiple news articles covering the same event. "
            f"Synthesize them into a single, comprehensive overview of 3-4 sentences. "
            f"Identify the core event and any significant variations or agreements:\n\n---\n{text}\n---\n\nOverall Summary:"
        )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI summary error: {e}"


# Collect Articles     


articles = []
article_info = []      # (source, title, url)
article_details = {}   # maps identifier -> {text, summary}

### NEW: First, get articles via RSS
print("\n=== Fetching articles via RSS ===")
for src, url in RSS_FEEDS.items():
    print(f"Fetching {src} …")
    items = collect_from_rss(src, url)
    print(f"  -> {len(items)} articles")
    for (s, title, link, text) in items:
        summary = generate_summary(text)
        ident = (s, title, link)
        articles.append(text)
        article_info.append(ident)
        article_details[ident] = {"text": text, "summary": summary}


### CHANGED: Still allow newspaper.build scraping if needed
sources = {
    "CNN": "https://www.cnn.com",
    "Guardian": "https://www.theguardian.com",
    "NYT": "https://www.nytimes.com",
    "NY Post": "https://nypost.com",
}

MAX_ARTICLES = 2000

print("\n=== Building newspapers ===")
for name, url in sources.items():
    print(f"\nBuilding {name} …")
    try:
        r = requests.get(url, headers={"User-Agent": config.browser_user_agent}, timeout=30)
        r.raise_for_status()
        paper = newspaper.build(url, config=config, memoize_articles=False, input_html=r.text)
    except Exception as e:
        print(f"  [!] Could not build {name}: {e}")
        continue

    count = 0
    for art in paper.articles:
        if count >= MAX_ARTICLES:
            break
        try:
            art.download()
            art.parse()
            if len(art.text.strip()) > 100:
                summary = generate_summary(art.text)
                ident = (name, art.title, art.url)
                articles.append(art.text)
                article_info.append(ident)
                article_details[ident] = {"text": art.text, "summary": summary}
                count += 1
        except (ArticleException, ArticleBinaryDataException):
            continue
        except Exception as e:
            print(f"  Skipped: {e}")
            continue

    print(f"  Collected {count} articles from {name}")

print(f"\nTotal articles gathered: {len(articles)}")

# END ARTICLE GATHERING

# START CLUSTERING


# --- Prepare structured articles for embeddings ---
structured_articles = []
for ident in article_info:  # ident = (source, title, url)
    info = article_details[ident]
    structured_articles.append({
        "title": ident[1],
        "summary": info["summary"],
        "source": ident[0],
        "text": info["text"]
    })

# --- Embeddings + Clustering ---
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from collections import defaultdict

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [a["summary"] for a in structured_articles]
embs = model.encode(texts)

clustering = AgglomerativeClustering(
    n_clusters=None,        # let algorithm decide
    distance_threshold=1.2, # adjust for topic tightness
    linkage="average"
).fit(embs)

labels = clustering.labels_

# --- Build clusters ---
clusters = defaultdict(list)
for art, label in zip(structured_articles, labels):
    clusters[label].append(art)

# --- Keep only one article per source per cluster ---
unique_by_source = {}
for cid, arts in clusters.items():
    keep = {}
    for a in arts:
        if a["source"] not in keep:
            keep[a["source"]] = a
    unique_by_source[cid] = list(keep.values())
clusters = unique_by_source

# --- Summarize each cluster using OpenAI ---
def summarize(text):
    return generate_summary(text, prompt_type="cluster")

output = {}
for idx, arts in clusters.items():
    cluster_text = " ".join(a["summary"] for a in arts)
    cluster_summary = summarize(cluster_text)
    output[f"Cluster {idx+1}"] = {
        "Summary of Cluster": cluster_summary,
        "Articles": arts
    }

with open("clusters.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"Saved {len(clusters)} clusters to clusters.json")
