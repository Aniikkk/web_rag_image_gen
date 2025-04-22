# Web RAG Image Generator

A web interface for the Web RAG (Retrieval Augmented Generation) Image Generation system.

## Features

- Web-based UI for entering prompts
- Real-time progress display
- Shows all the terminal output in the browser
- Displays the final generated image

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Download the Spacy model:

```bash
python -m spacy download en_core_web_sm
```

3. Start the Flask server:

```bash
python app.py
```

4. Open a browser and go to [http://localhost:5000](http://localhost:5000)

## How to Use

1. Enter a descriptive prompt in the input field (e.g., "A car in the mountains at sunset")
2. Select the number of reference images to retrieve (default is 3)
3. Click "Generate Image"
4. Watch the real-time progress in the log window
5. Once generation is complete, the final image will be displayed

## System Requirements

- Python 3.8 or higher
- CUDA-capable GPU recommended for faster image generation
- Internet connection (for web retrieval)

## Project Structure

- `app.py` - Flask server for the web interface
- `templates/` - HTML templates
- `static/` - CSS and JavaScript files
- `src/` - Core image generation and retrieval code

## Full Pipeline Architecture

The Web RAG Image Generator works through a sophisticated pipeline that combines web retrieval, text enhancement, and AI image generation. Here's how it works behind the scenes:

### 1. User Input Processing
- User submits a prompt through the web interface
- The Flask server receives the request and initiates the generation pipeline

### 2. Information Retrieval Phase
- **Entity Extraction**: The system uses NLP (spaCy) to identify key entities from the user prompt
- **Text Retrieval**:
  - Searches Wikipedia and news sources for information about the extracted entities
  - Extracts relevant content to provide context for the image generation
- **Image Retrieval**:
  - Uses Google Image Search API to find reference images related to the prompt
  - Downloads the top matching images to use as references

### 3. Prompt Enhancement
- Combines the original user prompt with extracted information
- Refines the prompt to be more detailed and context-aware
- This enhanced prompt improves the quality and relevance of the generated image

### 4. Image Preprocessing
- **Canny Edge Detection**: Processes downloaded reference images to extract edge information
- **Depth Map Extraction**: Uses the DPT model to create depth maps from the reference images
- These processed images serve as control inputs for the ControlNet model

### 5. AI Image Generation
- Uses Stable Diffusion with ControlNet conditioning
- Takes three inputs:
  - The enhanced text prompt
  - Edge detection maps from reference images
  - Depth maps from reference images
- Generates a high-quality image that combines the text prompt with visual elements from reference images

### 6. Result Delivery
- The generated image is saved to disk
- The web interface displays the final image along with the complete log of the generation process

### Data Flow

```
User Prompt → Entity Extraction → Web Retrieval (Text + Images) → 
Prompt Enhancement → Image Preprocessing → 
ControlNet Image Generation → Final Image
```

### Technical Implementation Details

- **Retrieval Pipeline**: 
  - `unified_retrieval()` coordinates all retrieval operations
  - Uses SerpAPI for Google Image Search
  - Implements robust error handling for failed downloads
  
- **Image Processing**:
  - OpenCV for Canny edge detection
  - Intel's DPT model for depth estimation
  - Processed images are stored in a standardized directory structure

- **Image Generation**:
  - Combines Stable Diffusion with ControlNet conditioning
  - Runs on GPU if available, falls back to CPU
  - Uses the processed control images to guide the generation

- **Web Interface**:
  - Flask server with Server-Sent Events (SSE) for real-time progress updates
  - JavaScript client receives and displays updates asynchronously
  - Responsive UI with error handling and visual feedback

---

