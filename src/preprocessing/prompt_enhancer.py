import os
import re
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)  # ✅ Add project root to Python path

from src.retrieval.text_retrieval import retrieve_text
from src.utils.logging import get_logger
logger = get_logger(__name__)

def extract_key_facts(text):
    """
    Extracts important words from the retrieved text.
    Uses regex to identify key capitalized words (e.g., names, brands, locations).
    """
    key_facts = re.findall(r'\b[A-Z][a-z]+\b', text)  # Extract capitalized words
    unique_facts = list(set(key_facts))[:10]  # Limit to 10 unique keywords
    return ", ".join(unique_facts)

def refine_prompt(user_prompt, query):
    """
    Enhances the user's prompt with retrieved text to make it more detailed.
    - Retrieves Wikipedia/News text for the query.
    - Extracts key information.
    - Combines it with the user's input.
    """
    retrieved_text = retrieve_text(query, use_cache=True)
    
    if not retrieved_text:
        logger.warning(f"❌ No retrieved text found for '{query}'. Using user prompt as-is.")
        return user_prompt
    
    key_facts = extract_key_facts(retrieved_text)
    
    # Merge the user prompt with key facts
    final_prompt = f"{user_prompt}, with {key_facts}"
    
    logger.info(f"🔹 Enhanced Prompt: {final_prompt}")
    return final_prompt

if __name__ == "__main__":
    # Example
    user_input = "Generate a cyberpunk Tesla Cybertruck with neon lights."
    query = "Tesla Cybertruck 2024"
    
    enhanced_prompt = refine_prompt(user_input, query)
    print("🔹 Final AI Prompt:", enhanced_prompt)
