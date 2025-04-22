import os
import sys
import time
import json
import threading
import io
import contextlib
from queue import Queue
from flask import Flask, render_template, request, Response, jsonify, send_from_directory

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Create Flask app
app = Flask(__name__)

# Ensure static and templates directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Queue for log messages
log_queue = Queue()

class LogCapture(io.StringIO):
    """Capture stdout and stderr and put it into a queue for SSE."""
    def write(self, s):
        if s.strip():  # Ignore empty strings
            log_queue.put(s)
        # Call the original write method
        return super().write(s)

def generate_images(prompt, num_images):
    """Run the image generation process and capture its output."""
    try:
        # Import the image generation function
        from src.generation.generate_image import generate_image
        from src.retrieval.retrieval_pipeline import unified_retrieval
        
        # Run the pipeline
        result = unified_retrieval(prompt, num_images=int(num_images))
        
        # Check if images were actually downloaded successfully
        if result and isinstance(result.get("images"), list) and len(result["images"]) > 0:
            # Use the first downloaded image
            image_path = result["images"][0]
            
            # Verify the image file exists
            if not os.path.exists(image_path):
                log_queue.put(f"Error: Downloaded image does not exist at path: {image_path}")
                return {"success": False, "error": f"Downloaded image not found at {image_path}"}
                
            # Extract the image ID from path
            image_id = os.path.basename(image_path).split('.')[0].split('_')[-1]
            # Extract folder name from image path
            folder_name = os.path.basename(os.path.dirname(image_path))
            
            # Generate image
            output_img_path = os.path.join(project_root, "data", "generated_images", 
                                        folder_name, f"generated_{image_id}.jpeg")
            
            generate_image(
                prompt=result["enhanced_prompt"],
                folder_name=folder_name,
                image_id=image_id,
                base_folder=os.path.join(project_root, "data")
            )
            
            # Check if the file exists
            if os.path.exists(output_img_path):
                # Return relative path for web serving
                return {"success": True, "image_path": f"/images/{folder_name}/generated_{image_id}.jpeg"}
            else:
                return {"success": False, "error": f"Generated image not found at {output_img_path}"}
        else:
            log_queue.put(f"No images were successfully downloaded. Please try a different prompt.")
            return {"success": False, "error": "No images were successfully downloaded"}
    
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        log_queue.put(error_msg)
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/generate')
def generate():
    """Generate images with SSE for real-time progress updates."""
    prompt = request.args.get('prompt', 'A car in the mountains at sunset')
    num_images = request.args.get('num_images', 3)
    
    # Clear the queue
    while not log_queue.empty():
        log_queue.get()
    
    def generate_events():
        # Start the generation process in a separate thread
        result_queue = Queue()
        
        def run_generation():
            # Redirect stdout/stderr to capture the logs
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = LogCapture()
            sys.stderr = sys.stdout
            
            try:
                result = generate_images(prompt, num_images)
                result_queue.put(result)
            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        
        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()
        
        # Send log messages as they arrive
        while thread.is_alive() or not log_queue.empty() or result_queue.empty():
            # Process log messages
            while not log_queue.empty():
                log_message = log_queue.get()
                event_data = json.dumps({"message": log_message})
                yield f"event: log\ndata: {event_data}\n\n"
            
            # Check if generation is complete
            if not result_queue.empty():
                result = result_queue.get()
                event_data = json.dumps(result)
                yield f"event: complete\ndata: {event_data}\n\n"
                break
            
            time.sleep(0.1)
    
    return Response(generate_events(), mimetype="text/event-stream")

@app.route('/images/<path:folder_name>/<path:filename>')
def serve_image(folder_name, filename):
    """Serve generated images."""
    return send_from_directory(os.path.join(project_root, 'data', 'generated_images', folder_name), 
                               filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, threaded=True) 