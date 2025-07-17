"""
News scraper fallback for additional news sources
"""
import requests
import trafilatura
from datetime import datetime
from typing import List, Dict
import re
from textblob import TextBlob

class NewsScraperFallback:
    """Fallback news scraper using web scraping"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_stock_news_fallback(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Fallback method to get stock news from web scraping
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of news articles to fetch
            
        Returns:
            List of news articles with sentiment analysis
        """
        try:
            # Try to scrape from Yahoo Finance news page
            url = f"https://finance.yahoo.com/quote/{symbol}/news"
            
            # This is a basic implementation - in production you'd want more robust scraping
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # Extract text content
                text_content = trafilatura.extract(response.text)
                
                if text_content:
                    # Create a basic news entry from the scraped content
                    sentiment_score, sentiment_label = self._analyze_sentiment(text_content)
                    
                    return [{
                        'title': f"{symbol} Market News Summary",
                        'summary': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                        'link': url,
                        'published': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'source': 'Yahoo Finance',
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'relevance': 0.8
                    }]
            
            return []
            
        except Exception as e:
            print(f"Error in news scraper fallback: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> tuple:
        """
        Analyze sentiment of given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        try:
            # Clean the text
            cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            
            # Convert polarity to label
            if polarity > 0.1:
                label = "Positive"
            elif polarity < -0.1:
                label = "Negative"
            else:
                label = "Neutral"
            
            return round(polarity, 3), label
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 0.0, "Neutral"