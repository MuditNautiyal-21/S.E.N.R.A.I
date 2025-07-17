import requests
import yfinance as yf
from textblob import TextBlob
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import re

class NewsSentimentAnalyzer:
    """Analyzes news sentiment for stocks using multiple sources"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.cache_expiry = timedelta(minutes=30)
    
    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Fetch news for a given stock symbol
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of news articles to fetch
            
        Returns:
            List of news articles with sentiment analysis
        """
        try:
            # Get news from Yahoo Finance
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                print(f"No news found for {symbol}")
                return []
            
            analyzed_news = []
            for article in news[:limit]:
                try:
                    # Extract data from the new Yahoo Finance API structure
                    content = article.get('content', article)
                    
                    title = content.get('title', '')
                    summary = content.get('summary', content.get('description', ''))
                    
                    # Skip if both title and summary are empty
                    if not title and not summary:
                        continue
                    
                    # Get link from various possible locations
                    link = ''
                    if 'canonicalUrl' in content:
                        link = content['canonicalUrl'].get('url', '')
                    elif 'clickThroughUrl' in content:
                        link = content['clickThroughUrl'].get('url', '')
                    elif 'link' in article:
                        link = article['link']
                    
                    # Get source
                    source = 'Yahoo Finance'
                    if 'provider' in content:
                        source = content['provider'].get('displayName', source)
                    elif 'publisher' in article:
                        source = article['publisher']
                    
                    # Get publish date
                    published = datetime.now().strftime("%Y-%m-%d %H:%M")
                    if 'pubDate' in content:
                        try:
                            pub_date = datetime.fromisoformat(content['pubDate'].replace('Z', '+00:00'))
                            published = pub_date.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    elif 'providerPublishTime' in article:
                        published = self._format_timestamp(article['providerPublishTime'])
                    
                    # Combine title and summary for sentiment analysis
                    text_for_analysis = f"{title} {summary}"
                    
                    # Perform sentiment analysis
                    sentiment_score, sentiment_label = self._analyze_sentiment(text_for_analysis)
                    
                    analyzed_news.append({
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'published': published,
                        'source': source,
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'relevance': self._calculate_relevance(text_for_analysis, symbol)
                    })
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
            
            return analyzed_news
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
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
    
    def _calculate_relevance(self, text: str, symbol: str) -> float:
        """
        Calculate how relevant the news is to the stock
        
        Args:
            text: News text
            symbol: Stock symbol
            
        Returns:
            Relevance score (0-1)
        """
        try:
            text_lower = text.lower()
            symbol_lower = symbol.lower()
            
            # Count mentions of symbol
            symbol_mentions = text_lower.count(symbol_lower)
            
            # Look for financial keywords
            financial_keywords = [
                'earnings', 'revenue', 'profit', 'loss', 'growth', 'dividend',
                'merger', 'acquisition', 'ipo', 'buyback', 'partnership',
                'contract', 'deal', 'investment', 'expansion', 'lawsuit'
            ]
            
            keyword_score = sum(1 for keyword in financial_keywords if keyword in text_lower)
            
            # Calculate relevance score
            relevance = min(1.0, (symbol_mentions * 0.3 + keyword_score * 0.1))
            
            return round(relevance, 2)
            
        except Exception:
            return 0.5  # Default relevance
    
    def _format_timestamp(self, timestamp: int) -> str:
        """
        Format timestamp to readable string
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted date string
        """
        try:
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M")
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def get_overall_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        Calculate overall sentiment from news list
        
        Args:
            news_list: List of analyzed news articles
            
        Returns:
            Dictionary with overall sentiment metrics
        """
        if not news_list:
            return {
                'overall_score': 0.0,
                'overall_label': 'Neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        scores = [article['sentiment_score'] for article in news_list]
        labels = [article['sentiment_label'] for article in news_list]
        
        overall_score = sum(scores) / len(scores)
        
        if overall_score > 0.1:
            overall_label = "Positive"
        elif overall_score < -0.1:
            overall_label = "Negative"
        else:
            overall_label = "Neutral"
        
        return {
            'overall_score': round(overall_score, 3),
            'overall_label': overall_label,
            'positive_count': labels.count('Positive'),
            'negative_count': labels.count('Negative'),
            'neutral_count': labels.count('Neutral'),
            'total_articles': len(news_list)
        }
    
    def get_sentiment_impact_on_price(self, sentiment_score: float) -> Dict:
        """
        Estimate potential price impact based on sentiment
        
        Args:
            sentiment_score: Overall sentiment score
            
        Returns:
            Dictionary with impact assessment
        """
        if sentiment_score > 0.5:
            impact = "Strong Positive"
            color = "green"
            expected_movement = "Upward pressure expected"
        elif sentiment_score > 0.2:
            impact = "Moderate Positive"
            color = "lightgreen"
            expected_movement = "Slight upward bias"
        elif sentiment_score < -0.5:
            impact = "Strong Negative"
            color = "red"
            expected_movement = "Downward pressure expected"
        elif sentiment_score < -0.2:
            impact = "Moderate Negative"
            color = "orange"
            expected_movement = "Slight downward bias"
        else:
            impact = "Neutral"
            color = "gray"
            expected_movement = "Minimal news impact"
        
        return {
            'impact_level': impact,
            'color': color,
            'expected_movement': expected_movement,
            'confidence': min(100, abs(sentiment_score) * 100)
        }