import sys
import os
import wikipediaapi


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from src.utils.logging import get_logger

logger = get_logger(__name__)  # Initialize logger

def get_wikipedia_summary(query, sentences=2):
    """Fetches a short summary from Wikipedia for the given query."""
    user_agent = "WebRAG-Bot/1.0 (contact: anikethanrao1414@gmail.com)" 
    wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent) 

    page = wiki_wiki.page(query)

    if not page.exists():
        logger.error(f"❌ Wikipedia page for '{query}' not found.")
        return None
    
    summary = page.summary[:sentences * 300]  # Approx. word count for n sentences
    logger.info(f"✅ Wikipedia summary retrieved for '{query}'")
    return summary

if __name__ == "__main__":
    query = "cat"
    wiki_text = get_wikipedia_summary(query)
    
    if wiki_text:
        logger.info(f"Wikipedia Summary:\n{wiki_text}")
    else:
        logger.error("❌ No Wikipedia summary found.")