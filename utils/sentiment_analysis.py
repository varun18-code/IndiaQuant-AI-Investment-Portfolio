import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re
import time

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analyzer"""
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text):
        """
        Analyze sentiment of text
        
        Parameters:
        text (str): Text to analyze
        
        Returns:
        dict: Sentiment scores
        """
        if not text or not isinstance(text, str):
            return {
                'neg': 0,
                'neu': 1,
                'pos': 0,
                'compound': 0
            }
        
        return self.sia.polarity_scores(text)
    
    def classify_sentiment(self, score):
        """
        Classify sentiment based on compound score
        
        Parameters:
        score (float): Compound sentiment score
        
        Returns:
        str: Sentiment classification
        """
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    def get_sentiment_color(self, score):
        """
        Get color based on sentiment score
        
        Parameters:
        score (float): Sentiment score
        
        Returns:
        str: Color hex code
        """
        if score >= 0.05:
            return "#4CAF50"  # Green for positive
        elif score <= -0.05:
            return "#F44336"  # Red for negative
        else:
            return "#9E9E9E"  # Gray for neutral


def fetch_financial_news(ticker, days=7, max_results=10):
    """
    Fetch financial news for a given ticker
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days to look back
    max_results (int): Maximum number of news articles to return
    
    Returns:
    list: List of news articles with title, date, url, and sentiment
    """
    # This is a mock implementation - in a real system, you would use a news API
    # such as Alpha Vantage, News API, or specialized financial news APIs
    
    # Let's create some mock data for demonstration purposes
    company_map = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft',
        'GOOGL': 'Google',
        'AMZN': 'Amazon',
        'TSLA': 'Tesla',
        'META': 'Meta',
        'NFLX': 'Netflix',
        'NVDA': 'NVIDIA',
        'IBM': 'IBM',
        'ORCL': 'Oracle'
    }
    
    company_name = company_map.get(ticker, ticker)
    
    # Create date range for the past 'days' days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Sample headlines based on the company
    positive_headlines = [
        f"{company_name} Reports Record Quarterly Earnings",
        f"Analysts Raise {company_name} Price Target After Strong Results",
        f"{company_name} Announces New Product Line",
        f"{company_name} Expands Into New Markets",
        f"Investors Bullish on {company_name}'s Growth Strategy"
    ]
    
    neutral_headlines = [
        f"{company_name} Holds Annual Shareholder Meeting",
        f"{company_name} CEO Discusses Industry Trends",
        f"{company_name} to Present at Upcoming Conference",
        f"{company_name} Maintains Market Position",
        f"{company_name} Announces Executive Changes"
    ]
    
    negative_headlines = [
        f"{company_name} Misses Earnings Expectations",
        f"{company_name} Faces Regulatory Scrutiny",
        f"Analysts Downgrade {company_name} Stock",
        f"{company_name} Announces Restructuring Plan",
        f"Competition Pressures {company_name}'s Market Share"
    ]
    
    # Combine headlines
    all_headlines = positive_headlines + neutral_headlines + negative_headlines
    
    # Generate random dates within the range
    dates = [start_date + timedelta(days=np.random.randint(0, days+1)) for _ in range(len(all_headlines))]
    dates.sort(reverse=True)  # Sort from newest to oldest
    
    # Generate random URLs
    urls = [f"https://example.com/finance/news/{ticker.lower()}/{i}" for i in range(len(all_headlines))]
    
    # Combine into news items
    news_items = []
    for i, headline in enumerate(all_headlines):
        if i >= max_results:
            break
        
        news_items.append({
            'title': headline,
            'date': dates[i].strftime('%Y-%m-%d'),
            'url': urls[i],
            'source': np.random.choice(['Financial Times', 'Bloomberg', 'CNBC', 'Wall Street Journal', 'Reuters'])
        })
    
    # Analyze sentiment
    analyzer = SentimentAnalyzer()
    for item in news_items:
        sentiment = analyzer.analyze_text(item['title'])
        item['sentiment_score'] = sentiment['compound']
        item['sentiment'] = analyzer.classify_sentiment(sentiment['compound'])
        item['sentiment_color'] = analyzer.get_sentiment_color(sentiment['compound'])
    
    return news_items

def analyze_news_sentiment(news_items):
    """
    Analyze overall sentiment from news items
    
    Parameters:
    news_items (list): List of news items with sentiment scores
    
    Returns:
    dict: Sentiment analysis results
    """
    if not news_items:
        return {
            'avg_sentiment': 0,
            'sentiment_distribution': {'Positive': 0, 'Neutral': 0, 'Negative': 0},
            'overall_sentiment': 'Neutral'
        }
    
    # Calculate average sentiment
    sentiment_scores = [item['sentiment_score'] for item in news_items]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    # Calculate sentiment distribution
    sentiment_distribution = {
        'Positive': sum(1 for item in news_items if item['sentiment'] == 'Positive'),
        'Neutral': sum(1 for item in news_items if item['sentiment'] == 'Neutral'),
        'Negative': sum(1 for item in news_items if item['sentiment'] == 'Negative')
    }
    
    # Convert to percentages
    total = len(news_items)
    sentiment_distribution = {k: (v / total) * 100 for k, v in sentiment_distribution.items()}
    
    # Determine overall sentiment
    analyzer = SentimentAnalyzer()
    overall_sentiment = analyzer.classify_sentiment(avg_sentiment)
    
    return {
        'avg_sentiment': avg_sentiment,
        'sentiment_distribution': sentiment_distribution,
        'overall_sentiment': overall_sentiment
    }

def fetch_social_media_sentiment(ticker, days=7):
    """
    Fetch social media sentiment for a given ticker
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days to look back
    
    Returns:
    dict: Social media sentiment data
    """
    # This is a mock implementation - in a real system, you would use
    # social media APIs or specialized financial sentiment APIs
    
    # Create a date range for the past 'days' days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    dates.reverse()  # Order from oldest to newest
    
    # Generate random sentiment scores for each day
    # Use a random walk to make the data more realistic
    sentiment_scores = []
    sentiment_volumes = []
    
    # Start with a neutral sentiment
    current_sentiment = 0
    current_volume = 100
    
    for _ in dates:
        # Random walk for sentiment (-0.2 to +0.2 change)
        current_sentiment += np.random.uniform(-0.2, 0.2)
        # Clamp sentiment between -1 and 1
        current_sentiment = max(-1, min(1, current_sentiment))
        sentiment_scores.append(current_sentiment)
        
        # Random walk for volume (80% to 120% change)
        current_volume *= np.random.uniform(0.8, 1.2)
        # Ensure volume is at least 50
        current_volume = max(50, current_volume)
        sentiment_volumes.append(int(current_volume))
    
    # Create dictionary with date, sentiment, and volume
    social_sentiment = {
        'dates': dates,
        'sentiment_scores': sentiment_scores,
        'sentiment_volumes': sentiment_volumes
    }
    
    # Calculate average sentiment
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    # Classify overall sentiment
    analyzer = SentimentAnalyzer()
    overall_sentiment = analyzer.classify_sentiment(avg_sentiment)
    
    # Add summary statistics
    social_sentiment['avg_sentiment'] = avg_sentiment
    social_sentiment['overall_sentiment'] = overall_sentiment
    
    return social_sentiment
