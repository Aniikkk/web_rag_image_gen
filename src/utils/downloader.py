import os
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm 

def download_images(image_urls, query, save_dir="data/images/", num_images=5):
    """Downloads images from URLs and saves them locally."""
    query_dir = os.path.join(save_dir, query.replace(" ", "_")) 
    os.makedirs(query_dir, exist_ok=True) 

    downloaded_files = []
    
    for i, url in tqdm(enumerate(image_urls[:num_images]), total=num_images, desc="Downloading"):
        try:
            response = requests.get(url, timeout=10) 
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img_format = img.format.lower() if img.format else "jpg"
                filename = os.path.join(query_dir, f"image_{i}.{img_format}")
                
                img.save(filename)
                downloaded_files.append(filename)
        
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
    
    return downloaded_files
