import os
import cv2
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image
import numpy as np
import sys

# Add the project root to the path when running the script directly
if __name__ == "__main__":
    # Get the absolute path to the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.insert(0, project_root)

# Get absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GENERATED_IMAGES_DIR = os.path.join(DATA_DIR, "generated_images")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

def get_image_paths(base_folder, folder_name, image_id):
    for ext in ["jpeg", "png"]:
        edge_path = os.path.join(base_folder, "processed_images", folder_name, f"canny_image_{image_id}.{ext}")
        depth_path = os.path.join(base_folder, "processed_images", folder_name, f"depth_image_{image_id}.{ext}")
        if os.path.exists(edge_path) and os.path.exists(depth_path):
            return edge_path, depth_path
    
    # If files not found, print the directory to help debug
    dir_path = os.path.join(base_folder, "processed_images", folder_name)
    if os.path.exists(dir_path):
        print(f"Directory exists: {dir_path}")
        print(f"Files in directory: {os.listdir(dir_path)}")
        
    raise FileNotFoundError(f"Edge or depth image not found for image_id: {image_id} in folder: {folder_name}")

def preprocess_control_image(image_path, mode="edge"):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    image = cv2.resize(image, (512, 512))
    image = np.expand_dims(image, axis=-1)
    image = np.repeat(image, 3, axis=-1)
    return Image.fromarray(image)

def generate_image(prompt, folder_name, image_id, base_folder=None):
    if base_folder is None:
        base_folder = DATA_DIR
        
    device = "cuda" if torch.cuda.is_available() else "cpu"

    edge_img_path, depth_img_path = get_image_paths(base_folder, folder_name, image_id)
    output_img_path = os.path.join(base_folder, "generated_images", folder_name, f"generated_{image_id}.jpeg")
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)

    edge_image = preprocess_control_image(edge_img_path, mode="edge")
    depth_image = preprocess_control_image(depth_img_path, mode="depth")

    controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_canny").to(device)
    pipeline = StableDiffusionControlNetPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", controlnet=controlnet).to(device)

    output = pipeline(prompt=prompt, image=edge_image).images[0]
    output.save(output_img_path)
    print(f"✅ Generated image saved at {output_img_path}")

# For running the file as a script
if __name__ == "__main__":
    # Import unified_retrieval from src.retrieval.retrieval_pipeline
    from src.retrieval.retrieval_pipeline import unified_retrieval

    user_prompt = "guy riding a tricycle"
    result = unified_retrieval(user_prompt, num_images=3)

    if result and result.get("images") and len(result["images"]) > 0:
        # Use the first downloaded image as the selected image
        image_path = result["images"][0]
        # Extract the image ID from the path
        image_id = os.path.basename(image_path).split('.')[0].split('_')[-1]
        # Extract folder name from the image path
        folder_name = os.path.basename(os.path.dirname(image_path))
        
        generate_image(
            prompt=result["enhanced_prompt"],
            folder_name=folder_name,
            image_id=image_id
        )
    else:
        print("❌ No valid image found for generation.")
