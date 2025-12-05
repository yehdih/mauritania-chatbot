"""
Utility functions for the chatbot
"""
import re


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def validate_language(text: str, lang: str) -> bool:
    """
    Validate if text is in the expected language
    
    Args:
        text: Text to validate
        lang: Expected language ('fr' or 'ar')
        
    Returns:
        True if text appears to be in the expected language
    """
    if not text:
        return False
    
    if lang == "ar":
        # Check for Arabic characters
        arabic_chars = bool(re.search(r'[\u0600-\u06FF]', text))
        # Also allow numbers and basic punctuation
        non_arabic_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
        return arabic_chars and non_arabic_chars < len(text) * 0.3
    else:
        # For French, check for Latin characters
        latin_chars = bool(re.search(r'[A-Za-z]', text))
        return latin_chars