import os

def get_image_paths(base_folder, folder_name, image_id):
    edge_path = os.path.join(base_folder, "processed_images", folder_name, f"canny_{image_id}.jpeg")
    depth_path = os.path.join(base_folder, "processed_images", folder_name, f"depth_{image_id}.jpeg")

    # Debugging
    assert os.path.exists(edge_path), f"Edge image not found: {edge_path}"
    assert os.path.exists(depth_path), f"Depth image not found: {depth_path}"

    return edge_path, depth_path

# Example usage
base_folder = "../../data"
folder_name = "A_futuristic_cyberpunk_Tesla_Cybertruck_d6f85a17"
image_id = "image_4"  # Change accordingly

edge_img_path, depth_img_path = get_image_paths(base_folder, folder_name, image_id)
