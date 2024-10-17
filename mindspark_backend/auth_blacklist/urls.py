from django.urls import path, include
from .views import BlacklistView

urlpatterns = [
    path('jwt/blacklist/', BlacklistView.as_view(), name='blacklist')
]
