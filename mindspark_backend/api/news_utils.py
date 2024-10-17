import requests
from datetime import datetime, timedelta

API_KEY = "e62e8108127042489827a2d8e6cfe6ef"

def fetch_defense_news(keywords=None):
    base_url = "https://newsapi.org/v2/everything"
    
    # Define default defense-related search terms
    keywords = "defense OR military OR security OR geopolitics OR strategy OR international relations OR 'national security' OR 'foreign policy'"
    
    # Set the request parameters
    params = {
        'q': keywords,  # Search query
        'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'sortBy': 'relevancy',  # Order by relevancy
        'apiKey': API_KEY,
        'language': 'en',  
        'pageSize': 5,# Restrict to English articles
    }
    
    # Make the request to News API
    response = requests.get(base_url, params=params)

    print(response.json())
    
    # Check for successful response
    if response.status_code == 200:
        return response.json()  # Return the articles
    else:
        return None  # Handle errors as needed
