"""
Configuration settings for the Mauritania Chatbot
"""

# API Configuration
GROQ_API_KEY = "your_api_key_here"  # Will be overridden by .env
GROQ_MODEL = "llama-3.3-70b-versatile"

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG Settings
RAG_TOP_K = 2
RAG_SIMILARITY_THRESHOLD = 0.30
RAG_MIN_SIMILARITY = 0.05

# Application Settings
APP_TITLE = "🇲🇷 مساعد الخدمات الموريتانية"
APP_DESCRIPTION = "Assistant Services Publics Mauritaniens"
APP_PORT = 7860
APP_HOST = "0.0.0.0"