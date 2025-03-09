import os
import sys
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR) 

from src.utils.downloader import download_images
from src.utils.logging import get_logger
from src.retrieval.image_retrieval import google_image_search
from src.retrieval.text_retrieval import retrieve_text

logger = get_logger(__name__)

load_dotenv(os.path.join(BASE_DIR, ".env"))

IMAGE_DIR = os.path.join(BASE_DIR, "data/images/")
TEXT_DIR = os.path.join(BASE_DIR, "data/text/")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def unified_retrieval(query, num_images=5, use_cache=True):
    """
    Retrieves both images & text for the given query.

    - Fetches images from Google/Bing
    - Retrieves Wikipedia & News text
    - Caches results to avoid redundant API calls
    """
    logger.info(f"🔍 Starting Unified Retrieval for '{query}'")

    text_data = retrieve_text(query, use_cache=use_cache)
    
    image_urls = google_image_search(query, num_images)
    
    if image_urls:
        logger.info(f"✅ Retrieved {len(image_urls)} images, downloading...")
        downloaded_images = download_images(image_urls, query, save_dir="../../data/images", num_images=num_images)
        logger.info(f"✅ Images saved at: {downloaded_images}")
    else:
        logger.warning(f"❌ No images found for '{query}'")

    text_file = os.path.join(TEXT_DIR, f"{query.replace(' ', '_')}.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text_data)

    logger.info(f"✅ Text saved at: {text_file}")

    return {
        "query": query,
        "text": text_data,
        "images": downloaded_images if image_urls else []
    }

if __name__ == "__main__":
    query = "travis Scott"
    result = unified_retrieval(query, num_images=5)

    if result["images"] or result["text"]:
        logger.info(f" Unified Retrieval Completed:\n{result}")
    else:
        logger.error(" Retrieval failed, no data found.")
