import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NEWS_API_KEY'),

def fetch_full_article(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # This part depends on the structure of the website you're scraping
        # Here's a general example that finds the article body
        article_text = ""
        for p in soup.find_all('p'):
            article_text += p.get_text()

        return article_text
    else:
        return None

def fetch_defense_news(keywords=None):
    base_url = "https://newsapi.org/v2/everything"
    
    # Define default defense-related search terms
   
    keywords = "international affairs"
    
    # Set the request parameters
    params = {
        'q': keywords,  # Search query
        'from': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        'sortBy': 'relevancy',  # Order by relevancy
        'apiKey': API_KEY,
        'language': 'en',  
        'pageSize': 1,
    }
    
    # Make the request to News API
    response = requests.get(base_url, params=params)

    print(response)

    # print(response.json())
    
    # Check for successful response
    if response.status_code == 200:
        return response.json()  # Return the articles
    else:
        return None  # Handle errors as needed
