import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv
load_dotenv()

import feedparser
import newspaper
from newspaper import Article, Config, ArticleException, ArticleBinaryDataException
from newspaper.mthreading import fetch_news
import requests
import warnings
import json
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

import google.generativeai as genai
from openai import OpenAI
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

def main():
    warnings.simplefilter(action="ignore", category=FutureWarning)
    # --- Supabase Setup ---
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # --- OpenAI Setup ---
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))



    # --- Gemini key check ---
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except AttributeError:
        print("="*50)
        print(">>> ERROR: Please set your GEMINI_API_KEY environment variable. <<<")
        print("="*50)
        exit()

    # --- Newspaper Config ---
    config = Config()
    config.memoize_articles = False
    config.browser_user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )

    # --- Constants ---
    CUTOFF = datetime.now(timezone.utc) - timedelta(hours=72)

    RSS_FEEDS = {
        "CNN": "http://rss.cnn.com/rss/cnn_latest.rss",
        "Guardian": "https://www.theguardian.com/world/rss",
        "NYPost": "https://nypost.com/feed/",
        "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "Politico": "https://rss.politico.com/politics-news.xml",
        "Politico - Congress": "https://rss.politico.com/congress.xml",
        "AlJazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "Fox": "https://feeds.foxnews.com/foxnews/latest",
        "CBS": "https://www.cbsnews.com/latest/rss/main",
        "ABC": "https://abcnews.go.com/abcnews/topstories"
    }

    NEWSPAPER_SOURCES = {
        "CNN": "https://www.cnn.com",
        "Guardian": "https://www.theguardian.com",
        "NYT": "https://www.nytimes.com",
        "NYPost": "https://nypost.com",
    }

    MAX_ARTICLES = 2000
    THREADS = 6  # Number of threads for multithreading

    # --- Helper Functions ---
    def article_exists(title: str) -> bool:
        """Check if an article title already exists in the database."""
        try:
            result = supabase.table("articles").select("title").eq("title", title).execute()
            return bool(result.data)
        except Exception as e:
            print(f"[!] Supabase check error: {e}")
            return False

    def collect_from_rss(src_url):
        src, url = src_url
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

    def generate_summary(text, prompt_type="article"):
        if not text or len(text.strip()) < 100:
            return "Not enough content to summarize."

        if prompt_type == "article":
            system_prompt = "You are a helpful assistant that summarizes news articles concisely."
            user_prompt = f"Summarize the following news article in 2-3 concise sentences:\n\n{text}"
        else:  # cluster
            system_prompt = "You are a helpful assistant that synthesizes multiple summaries into a coherent overview."
            user_prompt = f"Synthesize the following summaries into 3-4 concise sentences:\n\n{text}"

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

    # Fetch RSS Articles with Multithreading 
    articles = []
    article_info = []      # (source, title, url)
    article_details = {}   # identifier -> {text, summary}

    print("\n=== Fetching articles via RSS (multithreaded) ===")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(collect_from_rss, item) for item in RSS_FEEDS.items()]
        for future in as_completed(futures):
            items = future.result()
            for (s, title, link, text) in items:
                if article_exists(title):
                    continue
                summary = generate_summary(text)
                ident = (s, title, link)
                articles.append(text)
                article_info.append(ident)
                article_details[ident] = {"text": text, "summary": summary}

    print(f"RSS fetched: {len(articles)} articles collected.")

    # Build Newspaper Sources
    print("\n=== Building newspaper sources ===")
    papers = []
    for name, url in NEWSPAPER_SOURCES.items():
        try:
            r = requests.get(url, headers={"User-Agent": config.browser_user_agent}, timeout=30)
            r.raise_for_status()
            paper = newspaper.build(url, config=config, memoize_articles=False, input_html=r.text)
            papers.append(paper)
        except Exception as e:
            print(f"Could not build {name}: {e}")

    # Multithreaded Newspaper Download
    fetch_news(papers, threads=THREADS)

    for paper in papers:
        count = 0
        for art in paper.articles:
            if count >= MAX_ARTICLES:
                break
            try:
                art.parse()
                if len(art.text.strip()) > 100:
                    summary = generate_summary(art.text)
                    ident = (paper.brand, art.title, art.url)
                    articles.append(art.text)
                    article_info.append(ident)
                    article_details[ident] = {"text": art.text, "summary": summary}
                    count += 1
            except Exception:
                continue
        print(f"Collected {count} articles from {paper.brand}")

    print(f"Total articles gathered: {len(articles)}")

    # Prepare  Articles for Clustering
    structured_articles = []
    for ident in article_info:
        info = article_details[ident]
        structured_articles.append({
            "title": ident[1],
            "article_summary": info["summary"],
            "source": ident[0],
            "text": info["text"],
        })

    # Embeddings + Clustering 
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [a["article_summary"] for a in structured_articles]
    embs = model.encode(texts)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=1.2,
        linkage="average"
    ).fit(embs)

    labels = clustering.labels_

    # Build Clusters 
    clusters = defaultdict(list)
    for art, label in zip(structured_articles, labels):
        clusters[label].append(art)

    unique_by_source = {}
    for cid, arts in clusters.items():
        keep = {}
        for a in arts:
            if a["source"] not in keep:
                keep[a["source"]] = a
        unique_by_source[cid] = list(keep.values())
    clusters = unique_by_source

    # Multithreaded Cluster Summarization
    def summarize_and_name_cluster(arts):
        """Generate cluster summary and a meaningful cluster name from it."""
        cluster_text = " ".join(a["article_summary"] for a in arts)
        summary = generate_summary(cluster_text, prompt_type="cluster")

        # Generate a concise cluster name using OpenAI
        name_prompt = f"Create a short, descriptive title (3-5 words) for the following news summary:\n\n{summary}"
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise titles."},
                    {"role": "user", "content": name_prompt},
                ],
                temperature=0.3,
                max_tokens=20
            )
            cluster_name = resp.choices[0].message.content.strip()
        except Exception as e:
            cluster_name = summary.split()[:5]  # fallback: first 5 words
            cluster_name = " ".join(cluster_name)

        return summary, cluster_name

    # Execute in parallel
    output = {}
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(summarize_and_name_cluster, arts): arts for arts in clusters.values()}
        for idx, future in enumerate(as_completed(futures), 1):
            arts = futures[future]
            cluster_summary, cluster_name = future.result()
            output[str(idx)] = {
                "cluster_name": cluster_name,
                "cluster_summary": cluster_summary,
                "articles": arts
            }

    with open("rawdata.json", "w") as f:
        json.dump(output, f, indent=4)

    print(f"Saved {len(clusters)} clusters with AI-generated names to rawdata.json")

from apscheduler.schedulers.background import BackgroundScheduler
import time

def my_function_to_time():
    main()
    print(f"Executing function at: {time.ctime()}")
    time.sleep(2) # Simulate some work
    print("Function execution complete.")

def timed_execution_wrapper():
    """
    Wrapper function to time the execution of my_function_to_time.
    """
    start_time = time.time()
    my_function_to_time()
    end_time = time.time()
    execution_duration = end_time - start_time
    print(f"Execution duration: {execution_duration:.4f} seconds")

# Create a scheduler
scheduler = BackgroundScheduler()

# Add the job to run every hour
# The 'cron' trigger with hour='*' means it runs every hour at the minute it's started,
# or you can specify a specific minute, e.g., hour='*', minute='0' for top of the hour.
scheduler.add_job(timed_execution_wrapper, trigger='cron', hour='*')

# Start the scheduler
scheduler.start()

print("Scheduler started. Function will execute every hour.")

try:
    # Keep the main thread alive so the scheduler can run in the background
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    # Shut down the scheduler cleanly on exit
    scheduler.shutdown()
    print("Scheduler shut down.")

