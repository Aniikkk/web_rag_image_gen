import sys
import os
import wikipediaapi
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.utils.logging import get_logger
from src.retrieval.config import NEWS_API_KEY

logger = get_logger(__name__)  # Initialize logger

# Load API keys from .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Set up Wikipedia API with a valid User-Agent
USER_AGENT = "WebRAG-Bot/1.0 (contact: your-email@example.com)"  # Replace with your email

# Define text storage directory in project root
TEXT_DIR = os.path.join(BASE_DIR, "data/text/")
os.makedirs(TEXT_DIR, exist_ok=True)  # Ensure directory exists


def get_wikipedia_summary(query, sentences=2):
    """Fetches a short summary from Wikipedia for the given query."""
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=USER_AGENT)
    page = wiki_wiki.page(query)

    if not page.exists():
        logger.error(f"❌ Wikipedia page for '{query}' not found.")
        return None

    summary = page.summary[:sentences * 300]  # Approx. word count for n sentences
    logger.info(f"✅ Wikipedia summary retrieved for '{query}'")
    return summary


def get_latest_news(query, num_articles=3):
    """Fetches the latest news headlines about the query."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": num_articles
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        logger.error(f"❌ NewsAPI Error: {response.status_code}, {response.text}")
        return []

    data = response.json()
    articles = data.get("articles", [])

    news_texts = [f"{article['title']} - {article['source']['name']}" for article in articles]
    logger.info(f"✅ Retrieved {len(news_texts)} news articles for '{query}'")
    return news_texts


def save_text(query, text, source, save_dir="./data/text/"):
    """Saves retrieved text to a file in the project root."""
    query_safe = query.replace(" ", "_")
    text_dir = os.path.join(BASE_DIR, save_dir)
    os.makedirs(text_dir, exist_ok=True)  # Ensure directory exists

    file_path = os.path.join(text_dir, f"{query_safe}_{source}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    logger.info(f"✅ Saved {source} text: {file_path}")


def load_cached_text(query, source, save_dir="./data/text/"):
    """Loads cached text if available."""
    query_safe = query.replace(" ", "_")
    text_dir = os.path.join(BASE_DIR, save_dir)
    file_path = os.path.join(text_dir, f"{query_safe}_{source}.txt")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            cached_text = f.read()
            logger.info(f"🔄 Loaded cached {source} text for '{query}'")
            return cached_text
    return None


def retrieve_text(query, use_cache=True):
    """Retrieves combined Wikipedia + News text, using cached data if available."""
    # Check cache first
    wiki_text = load_cached_text(query, "wikipedia") if use_cache else None
    news_text = load_cached_text(query, "news") if use_cache else None

    # If not cached, fetch from the web
    if not wiki_text:
        wiki_text = get_wikipedia_summary(query) or ""
        save_text(query, wiki_text, "wikipedia")

    if not news_text:
        news_texts = get_latest_news(query)
        news_text = " ".join(news_texts)
        save_text(query, news_text, "news")

    combined_text = f"Wikipedia: {wiki_text}\n\nNews: {news_text}"
    return combined_text


if __name__ == "__main__":
    query = "ipod"
    text_data = retrieve_text(query)

    if text_data:
        logger.info(f"📄 Combined Retrieved Text:\n{text_data}")
    else:
        logger.error("❌ No text data found.")