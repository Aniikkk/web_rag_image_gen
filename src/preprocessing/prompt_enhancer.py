import os
import sys
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Fix module path to include project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from src.retrieval.text_retrieval import retrieve_text
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

def extract_key_facts(text):
    """
    Extracts key entities from the retrieved text using Named Entity Recognition (NER).
    Extracts descriptive words using TF-IDF.
    Returns a merged set of important keywords.
    """
    # Step 1: Extract Named Entities (People, Brands, Locations, Products, Dates)
    doc = nlp(text)
    named_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "PRODUCT", "DATE", "EVENT", "PERSON"]]
    
    # Step 2: Extract Important Descriptive Words using TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english", max_features=10)
    tfidf_matrix = vectorizer.fit_transform([text])
    tfidf_keywords = vectorizer.get_feature_names_out()
    
    # Step 3: Merge & Deduplicate Keywords
    key_facts = list(set(named_entities + list(tfidf_keywords)))  # Remove duplicates
    return ", ".join(key_facts[:10])  # Limit to 10 key facts

def refine_prompt(user_prompt, query):
    """
    Enhances the user's prompt with retrieved text by extracting key facts.
    - Retrieves Wikipedia/News text for the query.
    - Extracts important entities & keywords using NER + TF-IDF.
    - Combines it with the user's input for a more structured AI prompt.
    """
    retrieved_text = retrieve_text(query, use_cache=True)
    
    if not retrieved_text:
        logger.warning(f"❌ No retrieved text found for '{query}'. Using user prompt as-is.")
        return user_prompt
    
    key_facts = extract_key_facts(retrieved_text)
    
    # Merge the user prompt with extracted facts
    final_prompt = f"{user_prompt}, with {key_facts}"
    
    logger.info(f"🔹 Enhanced Prompt: {final_prompt}")
    return final_prompt

if __name__ == "__main__":
    # Example Test
    user_input = "travis scott with new iphone 16 pro"
    query = "iphone 16 pro"
    
    enhanced_prompt = refine_prompt(user_input, query)
    print("🔹 Final AI Prompt:", enhanced_prompt)
