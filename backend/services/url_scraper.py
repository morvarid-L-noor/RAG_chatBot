import requests
from bs4 import BeautifulSoup
from newspaper import Article
from typing import Optional

def scrape_url_content(url: str) -> str:
    """
    Scrape content from a URL using newspaper3k and BeautifulSoup as fallback
    
    Args:
        url: URL to scrape
        
    Returns:
        Scraped text content
    """
    try:
        # Try using newspaper3k first (better for articles)
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text and len(article.text.strip()) > 50:
            return article.text.strip()
        
        # Fallback to BeautifulSoup
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error scraping URL: {str(e)}")

