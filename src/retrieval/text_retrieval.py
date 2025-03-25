import wikipediaapi
import requests
import spacy
import re
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from src.utils.logging import get_logger
logger = get_logger(__name__)

nlp = spacy.load("en_core_web_sm")

USER_AGENT = "WebRAG-Bot/1.0 (contact: anikethanra1414@gmail.com)" 

wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=USER_AGENT)

NEWS_API_KEY = "1f8369a8ce8246a8a7ddc6395cf0aaba"

def extract_keywords(user_input):
    """
    Extract key topics from user input using Named Entity Recognition (NER) + TF-IDF.
    """
    doc = nlp(user_input)

    named_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "GPE", "EVENT", "PERSON"]]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5)
    tfidf_matrix = vectorizer.fit_transform([user_input])
    tfidf_keywords = vectorizer.get_feature_names_out()

    key_terms = list(set(named_entities + list(tfidf_keywords)))
    return key_terms if key_terms else [user_input]  # Return original input if extraction fails

def find_best_wikipedia_topic(key_terms):
    """
    Checks if a Wikipedia article exists for the most relevant topic.
    Falls back to broader searches if the exact topic does not exist.
    """
    for term in key_terms:
        page = wiki_wiki.page(term)
        if page.exists():
            logger.info(f"\n Found Wikipedia page for: {term}")
            return term 
    logger.warning(f"\n No exact Wikipedia match found for: {key_terms}. Using most general term: {key_terms[-1]}")
    return key_terms[-1] 

def get_wikipedia_summary(query):
    """
    Retrieves Wikipedia summary for the best available topic.
    """
    page = wiki_wiki.page(query)

    if not page.exists():
        logger.error(f" Wikipedia page for '{query}' not found.")
        return None

    summary = page.summary[:1000]  # Limit text length
    return summary

def get_news_articles(query, num_articles=3):
    """
    Fetches the latest news articles related to the best available topic.
    """
    query = find_best_wikipedia_topic(query.split()) 
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
        logger.error(f"\n NewsAPI Error: {response.status_code}, {response.text}")
        return []

    data = response.json()
    articles = data.get("articles", [])

    return [article["title"] for article in articles if "title" in article]

def retrieve_text(user_input):
    """
    Retrieves Wikipedia and News text for the most relevant topic extracted from the user input.
    """
    key_terms = extract_keywords(user_input) 
    query = find_best_wikipedia_topic(key_terms)

    wiki_text = get_wikipedia_summary(query) or ""
    news_texts = get_news_articles(query)

    combined_text = f"Wikipedia: {wiki_text}\n\nNews: {' '.join(news_texts)}"
    return combined_text
