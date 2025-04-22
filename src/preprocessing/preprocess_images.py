import os
import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from transformers import DPTFeatureExtractor, DPTForDepthEstimation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "../data/images/")
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed_images/")
os.makedirs(PROCESSED_DIR, exist_ok=True)

feature_extractor = DPTFeatureExtractor.from_pretrained("Intel/dpt-large")
depth_model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")
depth_model.eval()

def convert_to_canny(image_path, save_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 100, 200)
    cv2.imwrite(save_path, edges)

def convert_to_depth(image_path, save_path):
    image = Image.open(image_path).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        depth = depth_model(**inputs).predicted_depth.squeeze().numpy()
    
    depth = (depth - np.min(depth)) / (np.max(depth) - np.min(depth)) * 255
    depth = depth.astype(np.uint8)
    
    cv2.imwrite(save_path, depth)

def preprocess_images(query_folder):
    """Processes all retrieved images for ControlNet."""
    query_dir = os.path.join(IMAGE_DIR, query_folder)
    processed_dir = os.path.join(PROCESSED_DIR, query_folder)
    os.makedirs(processed_dir, exist_ok=True)

    if not os.path.exists(query_dir):
        print(f"❌ Directory not found: {query_dir}")
        return []

    image_files = [f for f in os.listdir(query_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not image_files:
        print(f"❌ No valid images found in directory: {query_dir}")
        return []
        
    processed_paths = []

    for img_file in image_files:
        try:
            img_path = os.path.join(query_dir, img_file)
            canny_path = os.path.join(processed_dir, f"canny_{img_file}")
            depth_path = os.path.join(processed_dir, f"depth_{img_file}")

            convert_to_canny(img_path, canny_path)
            convert_to_depth(img_path, depth_path)

            processed_paths.append(canny_path)
            processed_paths.append(depth_path)
        except Exception as e:
            print(f"❌ Error processing image {img_file}: {str(e)}")
            continue

    if processed_paths:
        print(f"✅ Processed {len(image_files)} images. Saved in {processed_dir}")
    else:
        print(f"❌ Failed to process any images from {query_dir}")
        
    return processed_paths

if __name__ == "__main__":
    query = "plan_b_electronic_city_abc1234"  # Replace with real folder name
    preprocess_images(query)
