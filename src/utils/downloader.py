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
    
    # Make sure we have valid image URLs
    if not image_urls or len(image_urls) == 0:
        print(f"No image URLs provided for downloading.")
        return downloaded_files
    
    for i, url in tqdm(enumerate(image_urls[:num_images]), total=min(len(image_urls), num_images), desc="Downloading"):
        try:
            response = requests.get(url, timeout=10) 
            if response.status_code != 200:
                print(f"\n Failed to download {url}: HTTP status code {response.status_code}")
                continue
                
            # Try to open the image to validate it
            try:
                img = Image.open(BytesIO(response.content))
                # Validate that this is actually an image
                img.verify()
                # Reopen after verify (which closes the file)
                img = Image.open(BytesIO(response.content))
                
                # Determine format and save
                img_format = img.format.lower() if img.format else "jpg"
                filename = os.path.join(query_dir, f"image_{i}.{img_format}")
                
                img.save(filename)
                downloaded_files.append(filename)
                
            except Exception as img_error:
                print(f"\n Failed to process image from {url}: {img_error}")
                continue
        
        except requests.exceptions.RequestException as e:
            print(f"\n Failed to download {url}: {e}")
            continue
        except Exception as e:
            print(f"\n Unexpected error downloading {url}: {e}")
            continue
    
    if not downloaded_files:
        print(f"Warning: No images were successfully downloaded from {len(image_urls)} URLs.")
    else:
        print(f"Successfully downloaded {len(downloaded_files)} images out of {min(len(image_urls), num_images)} attempted.")
        
    return downloaded_files
