# views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework import generics
from qdrant_client.http.exceptions import UnexpectedResponse
from django.db import DatabaseError
from django.contrib.auth import get_user_model
from .serializers import *
from .models import *
from .pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from .utils import *
import logging
from .news_utils import *

from .qdrant_utils import *

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):

        data = {
            'user': request.user.id,
            'article': request.data.get('article'),
        }

        serializer = self.get_serializer(data=data)
        
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)
        
        # Return the serialized data with a 201 response (created)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):

        data = { 
            "user": request.user.id, 
            "feedback": request.data.get("feedback"),
            "rating": request.data.get("rating"),
            "article": request.data.get("article"),
        }

        serializer = self.get_serializer(data=data)
        
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user) 
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all().order_by('-published_at')

    filter_backends = [filters.SearchFilter]
    search_fields = ['source', 'author', 'title', 'description', 'url', 'content', 'category', 'full_content']
    ordering_fields=['title']
    pagination_class = CustomPageNumberPagination


    def create(self, request, *args, **kwargs):
        
        articles_data = fetch_defense_news(request.data.get("keywords"))

        if articles_data:
            for article_data in articles_data.get('articles', []):
                article_data_dict = {
                    'source': article_data['source']['name'],
                    'author': article_data.get('author'),
                    'title': article_data['title'],
                    'description': article_data.get('description'),
                    'url': article_data['url'],
                    'url_to_image': article_data.get('urlToImage'),
                    'published_at': article_data['publishedAt'][:10],  # Trim timestamp to date
                    'content': article_data['content'],
                    'category': 'Defense',
                    'full_content': article_data.get('content', article_data.get('description'))
                }

                # Serialize the article data
                serializer = ArticleSerializer(data=article_data_dict)

                if serializer.is_valid():
                    serializer.save()
                else:
                    print(f"Skipping article: {serializer.errors}") 

            transfer_articles_to_qdrant()
        

        return Response({"message": "Data fetched successfully"}, status=status.HTTP_201_CREATED)

class SummaryAPIView(APIView):
    
    def get(self, request, article_id):
        try:
            # Retrieve the article by ID
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generate summary for the article
        summary = generate_summary(article)

        # Return the summary with a 200 OK status
        return Response({"summary": summary}, status=status.HTTP_200_OK)
    


class SentimentAnalysisAPIView(APIView):
    def get(self, request, article_id):
        # Retrieve the article by ID
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=404)

        # Analyze sentiment
        sentiment = analyze_sentiment(article)

        return Response({"sentiment": sentiment}, status=200)
    


class WordCloudAPIView(APIView):
    def get(self, request, article_id):
        # Retrieve the article by ID
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=404)

        # Generate and display the word cloud
        wordcloud = generate_word_cloud(article)

        return wordcloud
    

logger = logging.getLogger(__name__)

class RecommendationArticlesAPIView(APIView):
    def get(self, request):
        # Get the highest-rated review for the current user
        top_review = Review.objects.filter(user=request.user).order_by("-rating", "-timestamp").first()

        if not top_review:
            return Response({"message": "No reviews found for the user."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve similar articles based on the top-rated review's article
        similar_article_ids = query_similar_articles(top_review.article.id)

        if not similar_article_ids:
            return Response({"message": "No similar articles found."}, status=status.HTTP_404_NOT_FOUND)

        similar_articles = Article.objects.filter(id__in=similar_article_ids).exclude(id = top_review.article.id)

        if similar_article_ids:

            # Serialize the article data
            articles_data = ArticleSerializer(similar_articles, many=True).data

        # Return the list of similar articles with complete information
        return Response(articles_data, status=status.HTTP_200_OK)
   