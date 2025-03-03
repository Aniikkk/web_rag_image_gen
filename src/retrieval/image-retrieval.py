import requests
import os
import sys
from dotenv import load_dotenv

# Fix module path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Load API key
load_dotenv(os.path.join(BASE_DIR, ".env"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def google_image_search(query, num_images=5):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "tbm": "isch",  # Image search mode
        "api_key": GOOGLE_API_KEY,
        "ijn": 0  # First page of results
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return []

    data = response.json()

    # Extract image URLs
    image_urls = []
    seen_urls = set()  # Prevent duplicate links

    for result in data.get("images_results", []):
        image_url = result.get("original")  # Get high-res image
        if image_url and image_url not in seen_urls:
            seen_urls.add(image_url)
            image_urls.append(image_url)
        
        if len(image_urls) >= num_images:  # Limit results
            break  

    return image_urls

if __name__ == "__main__":
    query = "Tesla Cybertruck 2024"
    images = google_image_search(query, num_images=5)
    print("Top Retrieved Images:", images)
