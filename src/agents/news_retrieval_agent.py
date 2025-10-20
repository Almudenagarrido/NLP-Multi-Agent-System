import os
import sys
import json
import requests
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.ticker_finder import get_ticker_from_company_name
except ImportError as e:
    def get_ticker_from_company_name(company_name):
        return None

load_dotenv()

class NewsRetrievalAgent:
    
    def __init__(self):
        self.available_sources = ['yahoo_finance', 'news_api']
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.news_api_base_url = "https://newsapi.org/v2/everything"
    
    def find_ticker(self, company_name):
        ticker = get_ticker_from_company_name(company_name)
        return ticker
    
    def get_company_name(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('longName', info.get('shortName', ticker))
        except:
            return ticker
    
    def get_news(self, company_name, source, limit_per_source=50, days_back=30):
        found_ticker = self.find_ticker(company_name)
        if found_ticker:
            ticker = found_ticker
        else:
            return []
        
        if source and source not in self.available_sources:
            return []
        
        try:
            if source:
                articles = self._fetch_from_source(ticker, source, limit_per_source, days_back)
            else:
                all_articles = []
                for src in self.available_sources:
                    articles = self._fetch_from_source(ticker, src, limit_per_source, days_back)
                    all_articles.extend(articles)
                articles = self._remove_duplicates(all_articles)
            
            return articles
                
        except Exception as e:
            return []
    
    def get_news_json(self, company_names, source=None, limit_per_source=50, days_back=30):
        
        if isinstance(company_names, str):
            company_names = [company_names]
        
        result = {
            "source": source if source else "combined",
            "retrieved_at": datetime.now().isoformat(),
            "data": {}
        }
        
        for company_name in company_names:
            ticker = self.find_ticker(company_name)
            if not ticker:
                continue
            
            news = self.get_news(company_name, source, limit_per_source, days_back)
            result["data"][ticker] = {
                "company_name": company_name,
                "articles": news
            }
        
        return result

    def save_news_to_csv(self, company_name, filename=None, source=None, limit_per_source=50, days_back=30):
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{company_name}_news_{timestamp}.csv"
        
        if not filename.startswith("../../data/raw/"):
            filename = os.path.join("../../data/raw/", filename)
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        articles = self.get_news(company_name, source, limit_per_source, days_back)
        
        if articles:
            df = pd.DataFrame(articles)
            df.to_csv(filename, index=False, encoding='utf-8')
            return filename
        else:
            return ""
    
    def get_news_dataframe(self, company_name, source, limit_per_source=50, days_back=30):
        
        articles = self.get_news(company_name, source, limit_per_source, days_back)
        return pd.DataFrame(articles)
    
    def _fetch_from_source(self, ticker, source, limit, days_back):
        
        if source == 'yahoo_finance':
            return self._get_yahoo_news(ticker, limit)
        elif source == 'news_api':
            return self._get_newsapi_news(ticker, limit, days_back)
        return []
    
    def _remove_duplicates(self, articles):
        
        seen = set()
        unique = []
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen and title != 'no title':
                seen.add(title)
                unique.append(article)
        
        return unique
    
    def _get_yahoo_news(self, ticker, limit):
        
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
                    
            articles = []
            for item in news[:limit]:
                content = item.get('content', {})
                provider = content.get('provider', {})
                publisher = provider.get('displayName', 'Unknown')
                pub_date = content.get('pubDate', '')
                if pub_date:
                    try:
                        published_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        published_date = published_dt.isoformat()
                    except:
                        published_date = pub_date
                else:
                    published_date = ''
                
                company_name = self.get_company_name(ticker)
                
                article_data = {
                    'title': content.get('title', 'No title'),
                    'publisher': publisher,
                    'link': content.get('canonicalUrl', {}).get('url', ''),
                    'published_date': published_date,
                    'summary': content.get('summary', ''),
                    'ticker': ticker,
                    'company_name': company_name,
                    'source': 'yahoo_finance'
                }
                
                if article_data['title'] != 'No title':
                    articles.append(article_data)
                
            return articles
            
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
            return []
    
    def _get_newsapi_news(self, ticker, limit, days_back):
        
        if not self.news_api_key:
            return []
            
        try:
            actual_days_back = min(days_back, 30)
            start_date = (datetime.now() - timedelta(days=actual_days_back)).strftime('%Y-%m-%d')
            
            company_name = self.get_company_name(ticker)
            query = f"{ticker} OR {company_name}"
            
            params = {
                'q': query,
                'from': start_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': limit,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(self.news_api_base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles_data = data.get('articles', [])
                
                articles = []
                for article in articles_data[:limit]:
                    articles.append({
                        'title': article.get('title', ''),
                        'publisher': article.get('source', {}).get('name', ''),
                        'link': article.get('url', ''),
                        'published_date': article.get('publishedAt', ''),
                        'summary': article.get('description', ''),
                        'content': article.get('content', ''),
                        'ticker': ticker,
                        'company_name': company_name,
                        'source': 'news_api'
                    })
                return articles
            else:
                return []
                
        except Exception as e:
            return []


def test_agent(show_json=True, save_csv=False):
    agent = NewsRetrievalAgent()
    
    print("\n🚀 INITIATING TEST OF NEWS RETRIEVAL AGENT")
    print("=" * 60)
    
    companies = ['Apple', 'Tesla', 'Microsoft', 'Amazon', 'Google']
    limit = 10
    days_back = 7
    
    json_data = agent.get_news_json(companies, limit_per_source=limit, days_back=days_back)
    
    print(f"\n🕒 Retrieved at: {json_data['retrieved_at']}")
    print(f"🌐 Source mode: {json_data['source']}")
    print(f"💼 Companies processed: {', '.join(json_data['data'].keys())}")
    
    print("\n--------------------------------------------")
    for ticker, data in json_data['data'].items():
        articles = data['articles']
        company_name = data['company_name']
        print(f"\n📈 {ticker} ({company_name}): {len(articles)} news articles found")
        for i, art in enumerate(articles[:3], start=1):
            title = art.get('title', 'No title')[:80]
            print(f"   {i:>2}. [{art['source']}] {title}...")
        if len(articles) > 3:
            print(f"   ... and {len(articles) - 3} more articles.")
    print("--------------------------------------------")
    
    if show_json:
        print("\n🧾 FULL JSON OUTPUT:")
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
    if save_csv:
        print("\n💾 SAVING TO CSV...")
        filename = agent.save_news_to_csv('Apple', limit_per_source=limit, days_back=days_back)
    
    print("\n✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    RUN_TEST = False
    
    if RUN_TEST:
        test_agent(show_json=True, save_csv=False)