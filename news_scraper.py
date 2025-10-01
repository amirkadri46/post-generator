import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import time

class NewsScraperModule:
    """Free news scraping from HN, Reddit, TechCrunch, VentureBeat"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def fetch_all_news(self, keywords: str, timeframe_days: int = 7, sources: List[str] = None) -> List[Dict]:
        """Fetch news from all sources and combine"""
        all_articles = []
        
        if sources is None:
            sources = ["Hacker News", "Reddit", "TechCrunch", "VentureBeat"]
        
        # Parse keywords - IMPORTANT: Empty string should result in empty list
        keyword_list = []
        if keywords and keywords.strip():
            keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
        
        print(f"\n{'='*60}")
        print(f"FETCH_ALL_NEWS CALLED")
        print(f"Sources: {sources}")
        print(f"Keywords: {keyword_list if keyword_list else 'None (showing all)'}")
        print(f"Timeframe: {timeframe_days} days")
        print(f"{'='*60}\n")
        
        # Fetch from each source
        if "Hacker News" in sources:
            try:
                print("[MAIN] Calling scrape_hackernews...")
                hn_articles = self.scrape_hackernews(keyword_list, timeframe_days)
                print(f"[MAIN] HN returned {len(hn_articles)} articles")
                all_articles.extend(hn_articles)
            except Exception as e:
                print(f"[MAIN] HN error: {e}")
        
        if "Reddit" in sources:
            try:
                print("[MAIN] Calling scrape_reddit...")
                reddit_articles = self.scrape_reddit(keyword_list, timeframe_days)
                print(f"[MAIN] Reddit returned {len(reddit_articles)} articles")
                all_articles.extend(reddit_articles)
            except Exception as e:
                print(f"[MAIN] Reddit error: {e}")
        
        if "TechCrunch" in sources:
            try:
                print("[MAIN] Calling scrape_techcrunch...")
                tc_articles = self.scrape_techcrunch(keyword_list, timeframe_days)
                print(f"[MAIN] TechCrunch returned {len(tc_articles)} articles")
                all_articles.extend(tc_articles)
            except Exception as e:
                print(f"[MAIN] TechCrunch error: {e}")
        
        if "VentureBeat" in sources:
            try:
                print("[MAIN] Calling scrape_venturebeat...")
                vb_articles = self.scrape_venturebeat(keyword_list, timeframe_days)
                print(f"[MAIN] VentureBeat returned {len(vb_articles)} articles")
                all_articles.extend(vb_articles)
            except Exception as e:
                print(f"[MAIN] VentureBeat error: {e}")
        
        print(f"\n[MAIN] TOTAL ARTICLES COLLECTED: {len(all_articles)}")
        
        # Sort by score/popularity
        sorted_articles = sorted(all_articles, key=lambda x: x.get('score', 0), reverse=True)
        print(f"[MAIN] Returning {len(sorted_articles)} articles after sorting\n")
        return sorted_articles
    
    def scrape_hackernews(self, keywords: List[str], days: int = 7) -> List[Dict]:
        """Scrape Hacker News top stories"""
        articles = []
        try:
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(url, timeout=10)
            story_ids = response.json()[:100]
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for story_id in story_ids[:30]:
                try:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story = requests.get(story_url, timeout=5).json()
                    
                    if not story or 'title' not in story:
                        continue
                    
                    story_date = datetime.fromtimestamp(story.get('time', 0))
                    if story_date < cutoff_date:
                        continue
                    
                    # FIXED: Only filter by keywords if keywords were provided
                    title_lower = story.get('title', '').lower()
                    if keywords and not any(kw in title_lower for kw in keywords):
                        continue
                    
                    articles.append({
                        'title': story.get('title'),
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                        'source': 'Hacker News',
                        'score': story.get('score', 0),
                        'date': story_date.strftime('%Y-%m-%d'),
                        'comments': story.get('descendants', 0)
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"[HN] ERROR: {e}")
        
        return articles
    
    def scrape_reddit(self, keywords: List[str], days: int = 7) -> List[Dict]:
        """Scrape Reddit r/artificial and r/technology"""
        articles = []
        subreddits = ['artificial', 'technology', 'machinelearning', 'OpenAI']
        
        try:
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/top/.json?t=week&limit=25"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            
                            if not title:
                                continue
                            
                            # FIXED: Only filter by keywords if keywords were provided
                            title_lower = title.lower()
                            if keywords and not any(kw in title_lower for kw in keywords):
                                continue
                            
                            articles.append({
                                'title': title,
                                'url': post_data.get('url', ''),
                                'source': f'Reddit r/{subreddit}',
                                'score': post_data.get('score', 0),
                                'date': datetime.fromtimestamp(
                                    post_data.get('created_utc', 0)
                                ).strftime('%Y-%m-%d'),
                                'comments': post_data.get('num_comments', 0)
                            })
                    
                    time.sleep(1)
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Reddit error: {e}")
        
        return articles
    
    def scrape_techcrunch(self, keywords: List[str], days: int = 7) -> List[Dict]:
        """Scrape TechCrunch using their RSS feed"""
        articles = []
        try:
            url = "https://techcrunch.com/feed/"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return articles
                
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=30)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    date_elem = item.find('pubDate')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get_text(strip=True)
                    
                    if not title or not link:
                        continue
                    
                    if date_elem:
                        date_str = date_elem.get_text(strip=True)
                        try:
                            from email.utils import parsedate_to_datetime
                            article_date = parsedate_to_datetime(date_str)
                            if article_date.replace(tzinfo=None) < cutoff_date:
                                continue
                            formatted_date = article_date.strftime('%Y-%m-%d')
                        except:
                            formatted_date = datetime.now().strftime('%Y-%m-%d')
                    else:
                        formatted_date = datetime.now().strftime('%Y-%m-%d')
                    
                    # FIXED: Only filter by keywords if keywords were provided
                    title_lower = title.lower()
                    if keywords and not any(kw in title_lower for kw in keywords):
                        continue
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'source': 'TechCrunch',
                        'score': 100,
                        'date': formatted_date,
                        'comments': 0
                    })
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"[TC] ERROR: {e}")
        
        return articles
    
    def scrape_venturebeat(self, keywords: List[str], days: int = 7) -> List[Dict]:
        """Scrape VentureBeat AI section"""
        articles = []
        try:
            url = "https://venturebeat.com/category/ai/"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return articles
                
            soup = BeautifulSoup(response.content, 'html.parser')
            article_elements = soup.find_all('article', limit=20)
            
            for article in article_elements:
                try:
                    title_elem = article.find('h2', class_='article-title')
                    if not title_elem:
                        title_elem = article.find('h3') or article.find('h2')
                    
                    if not title_elem:
                        continue
                    
                    link_elem = title_elem.find('a')
                    if not link_elem:
                        continue
                    
                    title = link_elem.get_text(strip=True)
                    if not title:
                        continue
                    
                    # FIXED: Only filter by keywords if keywords were provided
                    title_lower = title.lower()
                    if keywords and not any(kw in title_lower for kw in keywords):
                        continue
                    
                    link = link_elem.get('href', '')
                    if not link:
                        continue
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'source': 'VentureBeat',
                        'score': 100,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'comments': 0
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"[VB] ERROR: {e}")
        
        return articles
    
    def extract_article_content(self, url: str) -> str:
        """Extract main content from article URL"""
        if not url:
            return ""
            
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return ""
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for script in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                script.decompose()
            
            selectors = [
                'article',
                '[class*="article-content"]',
                '[class*="post-content"]',
                '[class*="entry-content"]',
                '[class*="story-body"]',
                'main'
            ]
            
            content = None
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if content:
                paragraphs = content.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                if text:
                    return text[:5000]
            
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text(strip=True) for p in paragraphs[:15] if p.get_text(strip=True)])
            return text[:5000] if text else ""
            
        except Exception as e:
            print(f"Content extraction error: {e}")
            return ""