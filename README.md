# Web-RAG for Real-Time Image Generation

**A Retrieval-Augmented Generation (RAG) pipeline for text-to-image synthesis using real-time web data**. This project retrieves **live image-text information** (Google Images, Wikipedia, News API) and uses **Stable Diffusion + ControlNet** for **context-aware AI-generated images**.

---

## Progress So Far

**Image Retrieval:** Implemented **Google Image Search (SerpAPI)** for fetching real-world images.  
**Text Retrieval:** Wikipedia & News API integration for **context-aware text data**.  
**Caching System:** Stores retrieved **images (`data/images/`) & text (`data/text/`)**.  
**Logging System:** Centralized **logs in `logs.txt`** for debugging & monitoring.
**Unified Retrieval:** Run `retrieval.py` to retrieve both image and text data together.

---
