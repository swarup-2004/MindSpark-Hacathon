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
from datetime import datetime, timezone, timedelta


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

        setinment = 0
        sentiment_result = analyze_sentiment(request.data.get("feedback"))

        if (len(sentiment_result) == 1):
            if sentiment_result[0].get("label") == "NEGATIVE":
                sentiment = -1
            
            elif sentiment_result[0].get("label") == "POSITIVE":
                sentiment = 1

        data = { 
            "user": request.user.id, 
            "feedback": request.data.get("feedback"),
            "rating": request.data.get("rating"),
            "article": request.data.get("article"),
            "sentiment": sentiment,
        }

        serializer = self.get_serializer(data=data)
        
        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user) 
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all().order_by('-published_at')

    filter_backends = [filters.SearchFilter]
    search_fields = ['source', 'author', 'title', 'description', 'url', 'category', 'full_content']
    ordering_fields=['title']
    pagination_class = CustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        # Get query parameters for search
        query_params = request.query_params.get('search', None)
        
        # Check if there is a search query and log the user's activity
        if query_params:
            keywords = query_params.split('+')

            print(keywords)

            for keyword in keywords:
                # Finding the similar keyword in the vector db
                result = find_similar_keyword(keyword)

                print(result)

                if result.get("score") > 0.70:
                    # If similar keyword exists, update it
                    similar_keyword = UserActivityLogs.objects.get(id=result.get("id"))
                    similar_keyword.count += 1
                    # Define an IST (Indian Standard Time) offset (UTC+5:30)
                    ist_offset = timedelta(hours=5, minutes=30)
                    ist_timezone = timezone(ist_offset)

                    # Get the current time in IST
                    now_ist = datetime.now(ist_timezone)
                    similar_keyword.timestamp = now_ist
                    similar_keyword.save()

                else:
                    # If similar keyword is not present, add it in the SQL database
                    new_keyword = UserActivityLogs.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        keyword=keyword,
                        count=1
                    )
                    add_keyword(new_keyword.id)

            # Capture similar articles
            similar_article_ids = similarity_search_using_keyword(query_params)

            if not similar_article_ids:
                return Response({"message": "No similar articles found."}, status=status.HTTP_404_NOT_FOUND)

            similar_articles = Article.objects.filter(id__in=similar_article_ids)

            if similar_articles:
                # Serialize the article data
                articles_data = ArticleSerializer(similar_articles, many=True).data

                # Return the list of similar articles
                return Response(articles_data, status=status.HTTP_200_OK)

        # Proceed with the regular GET request functionality (list view)
        return super().list(request, *args, **kwargs)



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
                    # 'content': article_data['content'],
                    'category': 'Defense',
                    'full_content': fetch_full_article(article_data['url']),
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
            article_full_content = Article.objects.get(id=article_id).full_content
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=404)

        # Analyze sentiment
        sentiment = analyze_sentiment(article_full_content)

        positive = 0
        negative = 0
        count = 0

        if sentiment:
            for val in sentiment:
                count += 1
                print(val.get("label"))
                if val.get("label") == "POSITIVE":
                    positive += 1
                else:
                    negative += 1

        return Response({"positive": positive / float(count), "negative": negative / float(count)}, status=200)
    


class WordCloudAPIView(APIView):
    def get(self, request, article_id=None):
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

        if similar_articles:

            # Serialize the article data
            articles_data = ArticleSerializer(similar_articles, many=True).data

            # Return the list of similar articles with complete information
            return Response(articles_data, status=status.HTTP_200_OK)
        
        return Response({"message": "Visit more articles"}, status=status.HTTP_200_OK)
    

class FakeNewsAPIView(APIView):

    def get(self, request, article_id=None):

        if article_id:
            article_data = Article.objects.get(id=article_id).full_content

            results = classify_news_articles_fake_or_not(article_data)

            return Response(results, status=status.HTTP_200_OK)

   