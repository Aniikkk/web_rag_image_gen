import os
import cv2
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image
import numpy as np

def get_image_paths(base_folder, folder_name, image_id):
    edge_path = os.path.join(base_folder, "processed_images", folder_name, f"canny_{image_id}.jpeg")
    depth_path = os.path.join(base_folder, "processed_images", folder_name, f"depth_{image_id}.jpeg")
    
    if not os.path.exists(edge_path):
        raise FileNotFoundError(f"Edge image not found: {edge_path}")
    if not os.path.exists(depth_path):
        raise FileNotFoundError(f"Depth image not found: {depth_path}")
    
    return edge_path, depth_path

def preprocess_control_image(image_path, mode="edge"):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    image = cv2.resize(image, (512, 512))
    image = np.expand_dims(image, axis=-1)
    image = np.repeat(image, 3, axis=-1)
    return Image.fromarray(image)

def generate_image(prompt, edge_path, depth_path, output_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    edge_image = preprocess_control_image(edge_path, mode="edge")
    depth_image = preprocess_control_image(depth_path, mode="depth")
    
    controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15_canny").to(device)
    pipeline = StableDiffusionControlNetPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", controlnet=controlnet).to(device)
    
    output = pipeline(prompt=prompt, image=edge_image).images[0]
    output.save(output_path)
    print(f"Generated image saved at {output_path}")

if __name__ == "__main__":
    base_folder = "../../data"
    folder_name = "a_cat_using_iphone16_pro_88446692"  # Change dynamically as needed
    image_id = "image_3"  # Change dynamically as needed
    
    edge_img_path, depth_img_path = get_image_paths(base_folder, folder_name, image_id)
    output_img_path = os.path.join(base_folder, "generated_images", folder_name, f"generated_{image_id}.jpeg")
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    
    test_prompt = "a cat using iphone16 pro"
    generate_image(test_prompt, edge_img_path, depth_img_path, output_img_path)
