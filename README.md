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

---

## Progress So Far

**Image Retrieval:** Implemented **Google Image Search (SerpAPI)** for fetching real-world images.  
**Text Retrieval:** Wikipedia & News API integration for **context-aware text data**.  
**Caching System:** Stores retrieved **images (`data/images/`) & text (`data/text/`)**.  
**Logging System:** Centralized **logs in `logs.txt`** for debugging & monitoring.    
**Unified Retrieval:** Run `retrieval.py` to retrieve both image and text data together.  
**Pre-process:** Pre-process retrived (Canny edge detection and MiDas for depth detection) images for ControlNet.

---
