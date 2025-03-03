import os
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm  # Progress bar

# Function to download images
def download_images(image_urls, query, save_dir="data/images/", num_images=5):
    """Downloads images from URLs and saves them locally."""
    query_dir = os.path.join(save_dir, query.replace(" ", "_"))  # Create query-based folder
    os.makedirs(query_dir, exist_ok=True)  # Ensure directory exists

    downloaded_files = []
    
    for i, url in tqdm(enumerate(image_urls[:num_images]), total=num_images, desc="Downloading"):
        try:
            response = requests.get(url, timeout=10)  # Set timeout to avoid delays
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))  # Convert response to an image
                img_format = img.format.lower() if img.format else "jpg"
                filename = os.path.join(query_dir, f"image_{i}.{img_format}")
                
                img.save(filename)  # Save image
                downloaded_files.append(filename)
        
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
    
    return downloaded_files
