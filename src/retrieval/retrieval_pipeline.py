import os
import sys
from dotenv import load_dotenv
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.utils.downloader import download_images
from src.utils.logging import get_logger
from src.retrieval.image_retrieval import google_image_search
from src.retrieval.text_retrieval import retrieve_text  
from src.preprocessing.preprocess_images import preprocess_images
from src.preprocessing.prompt_enhancer import refine_prompt, extract_entities  

logger = get_logger(__name__)

load_dotenv(os.path.join(BASE_DIR, ".env"))

IMAGE_DIR = os.path.join(BASE_DIR, "data/images/")
TEXT_DIR = os.path.join(BASE_DIR, "data/text/")
PROCESSED_DIR = os.path.join(BASE_DIR, "data/processed_images/")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def shorten_filename(text, length=50):
    """Shorten a filename by taking the first few words and adding a hash for uniqueness."""
    short_text = "_".join(text.split()[:5])  # Use only the first 5 words
    unique_hash = hashlib.md5(text.encode()).hexdigest()[:8]  # Add an 8-char hash
    return f"{short_text}_{unique_hash}"

def unified_retrieval(user_prompt, num_images=5):
    """
    Retrieves images & text for the given query, enhances user input, and preprocesses images for ControlNet.

    - Extracts key query words from user input using enhanced entity detection.
    - Retrieves Wikipedia & News text based on extracted keywords.
    - Extracts key facts & merges them with user input.
    - Fetches images from Google/Bing and preprocesses them for ControlNet.
    - Returns the enhanced prompt for AI image generation.
    """
    logger.info(f"🔍 Starting Retrieval for User Prompt: '{user_prompt}'")

    #  Extract key entities from the user prompt
    extracted_entities = extract_entities(user_prompt)
    logger.info(f"🔍 Extracted Entities for Wikipedia: {extracted_entities}")

    # Retrieve Wikipedia & News Data
    retrieved_texts = []
    for entity in extracted_entities:
        entity_text = retrieve_text(entity) 
        if entity_text:
            retrieved_texts.append(f"{entity}: {entity_text[:200]}")

    wiki_news_text = " | ".join(retrieved_texts) if retrieved_texts else ""
    logger.info(f"\n Retrieved Wikipedia & News Data:\n{wiki_news_text[:500]}...") 

    # Enhance the user prompt using extracted key facts
    final_prompt = refine_prompt(user_prompt)
    logger.info(f"\n Final Enhanced AI Prompt: {final_prompt}")

    # Print the final AI prompt explicitly
    print(f"\n FINAL AI PROMPT:", final_prompt, "\n")

    save_dir_name = shorten_filename(final_prompt)

    # Retrieve Image Data
    query = final_prompt 
    image_urls = google_image_search(query, num_images)

    if image_urls:
        logger.info(f" Retrieved {len(image_urls)} images, downloading...")
        downloaded_images = download_images(image_urls, save_dir_name, save_dir="../../data/images", num_images=num_images)
        logger.info(f" Images saved at: {downloaded_images}")

        # Preprocess Images for ControlNet
        preprocess_images(save_dir_name)
        logger.info(f"\n Processed images saved in {PROCESSED_DIR}{save_dir_name}/")
    else:
        logger.warning(f"\n No images found for '{query}'")

    return {
        "user_prompt": user_prompt,
        "extracted_entities": extracted_entities,
        "enhanced_prompt": final_prompt,
        "wiki_news_text": wiki_news_text,
        "images": downloaded_images if image_urls else [],
        "processed_images": f"{PROCESSED_DIR}{save_dir_name}/"
    }

if __name__ == "__main__":
    user_prompt = "a tesla cybertruck with neon lights in cyberpunk setting"
    result = unified_retrieval(user_prompt, num_images=5)

    if result["images"]:
        logger.info(f"\n Retrieval & Prompt Enhancement Completed:\n{result}")
    else:
        logger.error(f"\n Retrieval failed, no data found.")
