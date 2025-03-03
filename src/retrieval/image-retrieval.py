import sys
import os
from dotenv import load_dotenv
import requests

# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)  # Add root to Python path

# Import the downloader module correctly
from src.utils.downloader import download_images

# Load API key from .env
load_dotenv(os.path.join(BASE_DIR, ".env"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def google_image_search(query, num_images=5):
    """Fetches image URLs from Google Image Search API (SerpAPI)."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "tbm": "isch",
        "api_key": GOOGLE_API_KEY,
        "ijn": 0  # First page of results
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}, {response.text}")
        return []

    data = response.json()
    image_urls = []

    seen_urls = set()  # Avoid duplicates
    for result in data.get("images_results", []):
        image_url = result.get("original")
        if image_url and image_url not in seen_urls:
            seen_urls.add(image_url)
            image_urls.append(image_url)
        if len(image_urls) >= num_images:
            break  # Stop once we have enough images
    
    return image_urls

if __name__ == "__main__":
    query = "Iphone 16 pro"
    num_images = 5
    images = google_image_search(query, num_images)
    
    if images:
        print(f"✅ Retrieved {len(images)} Images, Downloading...")
        downloaded_files = download_images(images, query, num_images=num_images)
        print(f"✅ Downloaded Files: {downloaded_files}")
    else:
        print("❌ No images found.")
