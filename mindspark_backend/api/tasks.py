# your_app/tasks.py
from celery import shared_task
from .models import Article
from .serializers import ArticleSerializer
from .news_utils import fetch_defense_news, fetch_full_article 
from .qdrant_utils import transfer_articles_to_qdrant

@shared_task
def fetch_and_store_articles(keywords):
    # Fetch articles using the provided keywords
    articles_data = fetch_defense_news(keywords)

    print(article_data)

    if articles_data:
        for article_data in articles_data.get('articles', []):
            article_data_dict = {
                'source': article_data['source']['name'],
                'author': article_data.get('author'),
                'title': article_data['title'],
                'description': article_data['description'],
                'url': article_data['url'],
                'url_to_image': article_data.get('urlToImage'),
                'published_at': article_data['publishedAt'][:10],  # Trim timestamp to date
                'category': 'Defense',
                'full_content': fetch_full_article(article_data['url']),
            }

            # Serialize and save the article
            serializer = ArticleSerializer(data=article_data_dict)
            if serializer.is_valid():
                serializer.save()
            else:
                print(f"Skipping article: {serializer.errors}")

        # After saving articles, transfer them to Qdrant
        transfer_articles_to_qdrant()
        return "Articles fetched, saved, and transferred to Qdrant."
    return "No articles found."
