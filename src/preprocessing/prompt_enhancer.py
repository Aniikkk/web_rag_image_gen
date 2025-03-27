import os
import sys
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from src.retrieval.text_retrieval import get_wikipedia_summary 
from src.utils.logging import get_logger
logger = get_logger(__name__)
nlp = spacy.load("en_core_web_sm")


def extract_entities(user_input):
    """
    Extracts named entities using:
    1. spaCy NER for known entities
    2. Dynamic product detection using POS tagging
    3. TF-IDF as a fallback for missing important words
    """
    doc = nlp(user_input)

    # Extract named entities using spaCy
    named_entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "GPE", "EVENT", "PERSON", "NORP"]]

    # Detect potential product names dynamically
    potential_products = []
    for token in doc:
        # Rule: Brand followed by a model name (e.g., "iPhone 16 Pro", "RTX 5090")
        if token.pos_ in ["PROPN", "NOUN"] and token.i < len(doc) - 1:
            next_token = doc[token.i + 1]
            if next_token.is_digit or next_token.text.lower() in ["pro", "max", "ultra", "ai", "quantum"]:
                potential_products.append(f"{token.text} {next_token.text}")

    # Fallback to TF-IDF if nothing was found
    if not named_entities and not potential_products:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=3)
        tfidf_matrix = vectorizer.fit_transform([user_input])
        tfidf_keywords = vectorizer.get_feature_names_out()
        fallback_keywords = list(tfidf_keywords)
    else:
        fallback_keywords = []

    # Combine all extracted terms
    key_terms = list(set(named_entities + potential_products + fallback_keywords))
    logger.info(f"🔍 Extracted Entities: {key_terms}")

    return key_terms if key_terms else [user_input]  # Return original input if extraction fails


def refine_prompt(user_prompt):
    """
    Enhances the user's prompt by retrieving context for each key entity that exists
    on Wikipedia, then merges that context with the original prompt.
    """
    # Extract entities from user input.
    entities = extract_entities(user_prompt)
    logger.info(f"🔍 Extracted Entities: {entities}")

    context_parts = []
    # For each entity, try to retrieve a Wikipedia summary.
    for entity in entities:
        summary = get_wikipedia_summary(entity)
        if summary:
            logger.info(f"\n Retrieved context for entity: {entity}")
            context_parts.append(f"{entity}: {summary[:350]}") 
        else:
            logger.info(f"ℹ\n No context found for entity: {entity}")

    # Merge the original prompt with the retrieved context.
    if context_parts:
        context_str = " | ".join(context_parts)
        final_prompt = f"{user_prompt}. Context: {context_str}"
    else:
        final_prompt = user_prompt

    logger.info(f"🔹 Final Enhanced Prompt: {final_prompt}")
    return final_prompt

if __name__ == "__main__":
    user_input = "multiheaded dog"

    enhanced_prompt = refine_prompt(user_input)
    print("\n Final AI Prompt:", enhanced_prompt)
