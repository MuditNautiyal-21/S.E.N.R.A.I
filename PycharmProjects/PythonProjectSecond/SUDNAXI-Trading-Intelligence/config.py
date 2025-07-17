"""
Configuration settings for the trading application
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Application configuration"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./trading_app.db')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    STREAMLIT_CONFIG = {
        'server.port': int(os.getenv('PORT', 8501)),
        'server.address': '0.0.0.0',
        'server.headless': True,
        'server.enableCORS': False,
        'server.enableXsrfProtection': False
    }
    
    INITIAL_BALANCE = 10000.0
    MAX_POSITION_SIZE = 0.35
    
    PRICE_REFRESH_INTERVAL = 60
    NEWS_REFRESH_INTERVAL = 300
    
    ENABLE_NEWS_SENTIMENT = True
    ENABLE_BACKTESTING = True
    ENABLE_ML_FEATURES = True
    ENABLE_REAL_TIME_LEARNING = True

config = Config()