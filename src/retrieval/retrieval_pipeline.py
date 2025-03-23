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
from src.preprocessing.preprocess_images import preprocess_images

logger = get_logger(__name__)

load_dotenv(os.path.join(BASE_DIR, ".env"))

IMAGE_DIR = os.path.join(BASE_DIR, "data/images/")
TEXT_DIR = os.path.join(BASE_DIR, "data/text/")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed_images/")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def unified_retrieval(query, num_images=5, use_cache=True):
    """
    Retrieves both images & text for the given query and preprocesses images for ControlNet.
    
    - Fetches images from Google/Bing
    - Retrieves Wikipedia & News text
    - Preprocesses retrieved images (Canny, Depth)
    - Caches results to avoid redundant API calls
    """
    logger.info(f"\nStarting Unified Retrieval for '{query}'")

    #Retrieve Text Data
    text_data = retrieve_text(query, use_cache=use_cache)

    #Retrieve Image Data
    image_urls = google_image_search(query, num_images)

    if image_urls:
        logger.info(f"\nRetrieved {len(image_urls)} images, downloading...")
        downloaded_images = download_images(image_urls, query, save_dir="../../data/images", num_images=num_images)
        logger.info(f"\nImages saved at: {downloaded_images}")

        #Preprocess Images for ControlNet
        preprocess_images(query)
        logger.info(f"\nProcessed images saved in {PROCESSED_DIR}{query.replace(' ', '_')}/")

    else:
        logger.warning(f"\nNo images found for '{query}'")

    #Save retrieved text in data/text/
    text_file = os.path.join(TEXT_DIR, f"{query.replace(' ', '_')}.txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text_data)

    logger.info(f"\nText saved at: {text_file}")

    return {
        "query": query,
        "text": text_data,
        "images": downloaded_images if image_urls else [],
        "processed_images": f"{PROCESSED_DIR}{query.replace(' ', '_')}/"
    }

if __name__ == "__main__":
    query = "nike travis scott highs"
    result = unified_retrieval(query, num_images=5)

    if result["images"] or result["text"]:
        logger.info(f"\nUnified Retrieval + Preprocessing Completed:\n{result}")
    else:
        logger.error("Retrieval failed, no data found.")
