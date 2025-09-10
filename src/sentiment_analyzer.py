import json
import os
from typing import Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv
import hashlib
import time

load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.cache_file = 'sentiment_cache.json'
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load sentiment cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save sentiment cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _generate_cache_key(self, ticker: str, news_data: Dict) -> str:
        """Generate cache key for news data"""
        # Create hash of ticker + headlines to check if news has changed
        content_string = ticker + str(sorted([
            item.get('headline', '') + item.get('summary', '') 
            for item in news_data.get('finviz_headlines', []) + news_data.get('yahoo_articles', [])
        ]))
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def analyze_sentiment(self, ticker: str, news_data: Dict) -> Dict:
        """Analyze sentiment of news data using Claude API"""
        
        # Check cache first
        cache_key = self._generate_cache_key(ticker, news_data)
        if cache_key in self.cache:
            print(f"Using cached sentiment analysis for {ticker}")
            return self.cache[cache_key]
        
        # Prepare news text for analysis
        news_text = self._prepare_news_text(news_data)
        
        if not news_text.strip():
            return {
                'sentiment_score': 50,  # Neutral score
                'sentiment_label': 'NEUTRAL',
                'confidence': 0,
                'reasoning': 'No news data available for analysis'
            }
        
        try:
            # Create prompt for Claude
            prompt = f"""
            Analyze the sentiment of the following financial news about {ticker} stock and provide a sentiment score.
            
            News Headlines and Articles:
            {news_text}
            
            Please analyze this news and provide:
            1. A sentiment score from 0-100 (0 = very negative, 50 = neutral, 100 = very positive)
            2. A sentiment label (POSITIVE, NEGATIVE, or NEUTRAL) 
            3. A confidence score from 0-100 (how confident you are in your analysis)
            4. Brief reasoning (2-3 sentences) explaining your sentiment assessment
            
            Focus on:
            - Overall tone and language used
            - Financial implications mentioned
            - Market outlook and analyst opinions
            - Company performance indicators
            - Future growth prospects
            
            Respond in JSON format:
            {{
                "sentiment_score": <number>,
                "sentiment_label": "<POSITIVE/NEGATIVE/NEUTRAL>",
                "confidence": <number>,
                "reasoning": "<brief explanation>"
            }}
            """
            
            # Make API call to Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Using cheaper model for cost efficiency
                max_tokens=500,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # Fallback parsing if JSON extraction fails
                    result = self._parse_response_fallback(response_text)
                
            except json.JSONDecodeError:
                result = self._parse_response_fallback(response_text)
            
            # Validate and clean result
            result = self._validate_sentiment_result(result)
            
            # Cache result
            self.cache[cache_key] = result
            self._save_cache()
            
            print(f"Sentiment analysis completed for {ticker}: {result['sentiment_label']} ({result['sentiment_score']})")
            
            return result
            
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {
                'sentiment_score': 50,
                'sentiment_label': 'NEUTRAL',
                'confidence': 0,
                'reasoning': f'Error in sentiment analysis: {str(e)}'
            }
    
    def _prepare_news_text(self, news_data: Dict) -> str:
        """Prepare news text for sentiment analysis"""
        text_parts = []
        
        # Add FinViz headlines
        for item in news_data.get('finviz_headlines', []):
            headline = item.get('headline', '')
            if headline:
                text_parts.append(f"HEADLINE: {headline}")
        
        # Add Yahoo Finance articles
        for item in news_data.get('yahoo_articles', []):
            headline = item.get('headline', '')
            summary = item.get('summary', '')
            content = item.get('content', '')
            
            if headline:
                text_parts.append(f"HEADLINE: {headline}")
            if summary:
                text_parts.append(f"SUMMARY: {summary}")
            if content:
                text_parts.append(f"CONTENT: {content[:500]}")  # Limit content length
        
        return '\n\n'.join(text_parts)
    
    def _parse_response_fallback(self, response_text: str) -> Dict:
        """Fallback parser for non-JSON responses"""
        result = {
            'sentiment_score': 50,
            'sentiment_label': 'NEUTRAL',
            'confidence': 50,
            'reasoning': 'Parsed from text response'
        }
        
        # Simple keyword-based sentiment detection
        positive_words = ['positive', 'bullish', 'growth', 'strong', 'buy', 'outperform', 'upgrade']
        negative_words = ['negative', 'bearish', 'decline', 'weak', 'sell', 'underperform', 'downgrade']
        
        text_lower = response_text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            result['sentiment_score'] = 70
            result['sentiment_label'] = 'POSITIVE'
        elif neg_count > pos_count:
            result['sentiment_score'] = 30
            result['sentiment_label'] = 'NEGATIVE'
        
        return result
    
    def _validate_sentiment_result(self, result: Dict) -> Dict:
        """Validate and clean sentiment analysis result"""
        # Ensure required keys exist
        if 'sentiment_score' not in result:
            result['sentiment_score'] = 50
        if 'sentiment_label' not in result:
            result['sentiment_label'] = 'NEUTRAL'
        if 'confidence' not in result:
            result['confidence'] = 50
        if 'reasoning' not in result:
            result['reasoning'] = 'No reasoning provided'
        
        # Clamp values to valid ranges
        result['sentiment_score'] = max(0, min(100, result['sentiment_score']))
        result['confidence'] = max(0, min(100, result['confidence']))
        
        # Ensure sentiment_label is valid
        valid_labels = ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
        if result['sentiment_label'] not in valid_labels:
            if result['sentiment_score'] > 60:
                result['sentiment_label'] = 'POSITIVE'
            elif result['sentiment_score'] < 40:
                result['sentiment_label'] = 'NEGATIVE'
            else:
                result['sentiment_label'] = 'NEUTRAL'
        
        return result