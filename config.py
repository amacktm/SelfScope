"""
Configuration settings for SelfScope
"""
import os

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-for-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///selfscope.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Local AI settings
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')  # Default model preference
    LM_STUDIO_URL = os.environ.get('LM_STUDIO_URL', 'http://localhost:1234/v1')
    LM_STUDIO_MODEL = os.environ.get('LM_STUDIO_MODEL', 'Hermes-3-Llama-3.2-3B')  # Your Hermes model
    
    # Alternative local AI endpoints
    LOCAL_AI_ENDPOINTS = [
        {'name': 'Ollama', 'url': OLLAMA_URL, 'enabled': True},
        # Add other local AI services here
        # {'name': 'LocalAI', 'url': 'http://localhost:8080', 'enabled': False},
        # {'name': 'Text-generation-webui', 'url': 'http://localhost:5000', 'enabled': False},
    ]
    
    # Journaling settings
    JOURNAL_DATA_DIR = os.environ.get('JOURNAL_DATA_DIR', 'journal_entries')
    MAX_ENTRY_LENGTH = int(os.environ.get('MAX_ENTRY_LENGTH', '5000'))
    
    # Analysis settings
    ENABLE_SENTIMENT_ANALYSIS = os.environ.get('ENABLE_SENTIMENT_ANALYSIS', 'True').lower() == 'true'
    ENABLE_THEME_DETECTION = os.environ.get('ENABLE_THEME_DETECTION', 'True').lower() == 'true'
    
    # UI settings
    DEFAULT_INSIGHT_MODE = os.environ.get('DEFAULT_INSIGHT_MODE', 'reflective')
    WORDS_PER_MINUTE_READING = int(os.environ.get('WORDS_PER_MINUTE_READING', '200'))