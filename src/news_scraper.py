import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import re

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_finviz_headlines(self, ticker: str) -> List[Dict[str, str]]:
        """Scrape headlines from FinViz"""
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headlines = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news table
            news_table = soup.find('table', {'id': 'news-table'})
            if not news_table:
                return headlines
            
            rows = news_table.find_all('tr')
            
            for row in rows[:10]:  # Get top 10 headlines
                cells = row.find_all('td')
                if len(cells) >= 2:
                    date_cell = cells[0]
                    headline_cell = cells[1]
                    
                    headline_link = headline_cell.find('a')
                    if headline_link:
                        headline_text = headline_link.get_text(strip=True)
                        link = headline_link.get('href', '')
                        
                        # Extract time info
                        time_text = date_cell.get_text(strip=True)
                        
                        headlines.append({
                            'source': 'FinViz',
                            'headline': headline_text,
                            'link': link,
                            'time': time_text
                        })
                        
        except Exception as e:
            print(f"Error scraping FinViz for {ticker}: {str(e)}")
            
        return headlines
    
    def scrape_yahoo_finance_news(self, ticker: str) -> List[Dict[str, str]]:
        """Scrape news from Yahoo Finance"""
        url = f"https://finance.yahoo.com/quote/{ticker}/"
        articles = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles - Yahoo Finance uses various selectors
            news_items = soup.find_all('li', class_=re.compile('js-stream-content'))
            
            if not news_items:
                # Try alternative selector
                news_items = soup.find_all('div', attrs={'data-test-locator': 'mega'})
            
            if not news_items:
                # Try finding articles by h3 headlines
                headlines = soup.find_all('h3')
                for h3 in headlines[:10]:
                    link_elem = h3.find('a')
                    if link_elem:
                        headline_text = h3.get_text(strip=True)
                        link = link_elem.get('href', '')
                        
                        if link.startswith('/'):
                            link = 'https://finance.yahoo.com' + link
                        
                        articles.append({
                            'source': 'Yahoo Finance',
                            'headline': headline_text,
                            'link': link,
                            'summary': ''
                        })
            else:
                for item in news_items[:10]:
                    headline_elem = item.find('h3') or item.find('a')
                    if headline_elem:
                        headline_text = headline_elem.get_text(strip=True)
                        link_elem = headline_elem if headline_elem.name == 'a' else headline_elem.find('a')
                        link = link_elem.get('href', '') if link_elem else ''
                        
                        if link.startswith('/'):
                            link = 'https://finance.yahoo.com' + link
                        
                        # Try to get summary
                        summary_elem = item.find('p')
                        summary = summary_elem.get_text(strip=True) if summary_elem else ''
                        
                        articles.append({
                            'source': 'Yahoo Finance',
                            'headline': headline_text,
                            'link': link,
                            'summary': summary
                        })
                        
        except Exception as e:
            print(f"Error scraping Yahoo Finance for {ticker}: {str(e)}")
            
        return articles
    
    def get_article_content(self, url: str) -> str:
        """Get full article content from URL"""
        try:
            if not url or url.startswith('#'):
                return ""
                
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find article content
            content_selectors = [
                'div[data-module="ArticleBody"]',
                '.caas-body',
                '.article-body',
                '.story-body',
                'article',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            if not content:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Clean and limit content
            content = re.sub(r'\s+', ' ', content)
            return content[:2000]  # Limit to 2000 chars to save API costs
            
        except Exception as e:
            print(f"Error fetching article content from {url}: {str(e)}")
            return ""
    
    def scrape_all_news(self, ticker: str) -> Dict[str, List[Dict]]:
        """Scrape news from all sources"""
        print(f"Scraping news for {ticker}...")
        
        finviz_headlines = self.scrape_finviz_headlines(ticker)
        time.sleep(1)  # Be respectful with requests
        
        yahoo_articles = self.scrape_yahoo_finance_news(ticker)
        time.sleep(1)
        
        # Get full content for a few top articles to analyze sentiment
        for article in yahoo_articles[:3]:
            if article['link']:
                article['content'] = self.get_article_content(article['link'])
                time.sleep(1)
        
        return {
            'finviz_headlines': finviz_headlines,
            'yahoo_articles': yahoo_articles,
            'total_items': len(finviz_headlines) + len(yahoo_articles)
        }