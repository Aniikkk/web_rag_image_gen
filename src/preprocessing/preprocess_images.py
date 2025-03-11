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
    """Converts an image to a Canny Edge Map."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(image, 100, 200)
    cv2.imwrite(save_path, edges)

def convert_to_depth(image_path, save_path):
    """Converts an image to a depth map using MiDaS."""
    image = Image.open(image_path).convert("RGB")
    inputs = feature_extractor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        depth = depth_model(**inputs).predicted_depth.squeeze().numpy()
    
    depth = (depth - np.min(depth)) / (np.max(depth) - np.min(depth)) * 255
    depth = depth.astype(np.uint8)
    
    cv2.imwrite(save_path, depth)

def preprocess_images(query):
    """Processes all retrieved images for ControlNet."""
    query_dir = os.path.join(IMAGE_DIR, query.replace(" ", "_"))
    processed_dir = os.path.join(PROCESSED_DIR, query.replace(" ", "_"))
    os.makedirs(processed_dir, exist_ok=True)

    for img_file in os.listdir(query_dir):
        img_path = os.path.join(query_dir, img_file)

        canny_path = os.path.join(processed_dir, f"canny_{img_file}")
        depth_path = os.path.join(processed_dir, f"depth_{img_file}")

        convert_to_canny(img_path, canny_path)
        convert_to_depth(img_path, depth_path)

    print(f"Processed images saved in {processed_dir}")

if __name__ == "__main__":
    query = "Tesla Cybertruck 2024"
    preprocess_images(query)

