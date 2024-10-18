# views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework import generics
from qdrant_client.http.exceptions import UnexpectedResponse
from rest_framework.pagination import PageNumberPagination
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
from collections import Counter
from django.db.models import Case, When
from rest_framework.permissions import AllowAny


from .qdrant_utils import *

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields =  ['id', 'user', 'article']
    # ordering_fields=['title']
    pagination_class = CustomPageNumberPagination
    
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

    filter_backends = [filters.SearchFilter]
    search_fields =  ['id', 'user', 'rating', 'feedback', 'article', 'sentiment']
    # ordering_fields=['title']
    pagination_class = CustomPageNumberPagination

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
        summary = generate_summary(article.full_content)

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
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        user = request.user

        # Fetch the top 5 review IDs from the Review model
        top_review_ids = list(
            Review.objects.filter(
                user=user, rating__gte=3, sentiment__gt=0  # Filter on rating and sentiment
            ).order_by("-rating", "-timestamp").values_list("article__id", flat=True)[:5]
        )

        # Fetch the top 5 search keywords from UserActivityLogs
        top_search_keywords = list(
            UserActivityLogs.objects.filter(
                user=user
            ).order_by("-count", "-timestamp").values_list("keyword", flat=True)[:5]
        )

        # If no review or search activity is found
        if not top_review_ids and not top_search_keywords:
            return Response(
                {"message": "No search activity or positive reviews found for the user."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Initialize a counter for occurrences of articles
        article_counter = Counter()

        # 1. Process Feedback (Top Reviews) with 60% weight
        if top_review_ids:
            for article_id in top_review_ids:
                review_article_similar_ids = query_similar_articles(article_id, 4)
                article_counter.update({article_id: 0.6 for article_id in review_article_similar_ids})

        # 2. Process Search Activity (Top Searches) with 40% weight
        if top_search_keywords:
            for keyword in top_search_keywords:
                search_related_article_ids = similarity_search_using_keyword(keyword, 4)
                article_counter.update({article_id: 0.4 for article_id in search_related_article_ids})

        # If no similar articles were found from both sources, return a message
        if not article_counter:
            return Response(
                {"message": "No similar articles found based on your search and review activity."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get article IDs sorted by weighted occurrence in descending order
        sorted_article_ids = [article_id for article_id, count in article_counter.most_common()]

        # Retrieve articles based on the sorted article IDs
        similar_articles = Article.objects.filter(id__in=sorted_article_ids)

        # Exclude articles that have been rated by the user in top reviews
        if top_review_ids:
            similar_articles = similar_articles.exclude(id__in=top_review_ids)

        # Paginate and return the response
        if similar_articles.exists():
            paginator = PageNumberPagination()
            paginator.page_size = 10  # Set the number of items per page

            # Order articles based on their appearance in the sorted list
            ordered_articles = similar_articles.filter(id__in=sorted_article_ids).order_by(
                Case(
                    *[When(id=article_id, then=pos) for pos, article_id in enumerate(sorted_article_ids)]
                )
            )

            paginated_articles = paginator.paginate_queryset(ordered_articles, request)

            # Serialize paginated articles
            serializer = ArticleSerializer(paginated_articles, many=True)

            # Return paginated response
            return paginator.get_paginated_response(serializer.data)

        return Response(
            {"message": "No articles found for your recent activity. Please engage more with the platform."},
            status=status.HTTP_200_OK
        )



    

class FakeNewsAPIView(APIView):

    

    def get(self, request, article_id=None):

        if article_id:
            article_data = Article.objects.get(id=article_id).full_content

            results = classify_news_articles_fake_or_not(article_data)

            return Response(results, status=status.HTTP_200_OK)
        
        return Response({"message": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
        


class SimilarArticlesAPIView(APIView):

    pagination_class = CustomPageNumberPagination

    # permission_classes = [IsAuthenticated]

    def get(self, request, article_id=None):

        if article_id:

            similar_article_ids = query_similar_articles(article_id, 3)

            if not similar_article_ids:
                return Response({"message": "No similar articles found."}, status=status.HTTP_404_NOT_FOUND)

            similar_articles = Article.objects.filter(id__in=similar_article_ids).exclude(id = article_id)

            if similar_articles:


                paginator = PageNumberPagination()
                paginator.page_size = 10  # Set the number of items per page
                paginated_articles = paginator.paginate_queryset(similar_articles, request)

                # Serialize paginated articles
                serializer = ArticleSerializer(paginated_articles, many=True)

                # Return paginated response
                return paginator.get_paginated_response(serializer.data)
            
        return Response({"message": "bad request"}, status=status.HTTP_400_BAD_REQUEST)
            



class ChromeExtensionAPIView(APIView):

    authentication_classes = []  
    permission_classes = [AllowAny]

    def get(self, request):

        url = request.query_params.get('url', None)

        print(url)
        if url:
            
            # Fetch the full article content based on the provided URL
            article_data = fetch_full_article(url)

            # Perform sentiment analysis on the article
            sentiment = analyze_sentiment(article_data)

            # Generate a summary for the article
            summary = generate_summary(article_data)

            positive = 0
            negative = 0
            count = 0

            # Iterate through sentiment analysis results
            if sentiment:
                for val in sentiment:
                    count += 1
                    print(val.get("label"))  # Debug print to view sentiment labels
                    if val.get("label") == "POSITIVE":
                        positive += 1
                    else:
                        negative += 1

            sentiment_results = {}

            # Calculate positive sentiment percentage
            if positive != 0 and count != 0:
                sentiment_results["positive"] = positive / float(count)

            # Calculate negative sentiment percentage
            if negative != 0 and count != 0:
                sentiment_results["negative"] = negative / float(count)

            # Return sentiment and summary data
            return Response({"sentiment": sentiment_results, "summary": summary}, status=status.HTTP_200_OK)

        # Handle case where no URL is provided
        return Response({"error": "Invalid URL"}, status=status.HTTP_400_BAD_REQUEST)
