# views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import *
from .models import *
from .pagination import CustomPageNumberPagination
from rest_framework.views import APIView
from .utils import *

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)
    

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ['source', 'author', 'title', 'description', 'url', 'content', 'category', 'full_content']
    ordering_fields=['title']
    pagination_class = CustomPageNumberPagination


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