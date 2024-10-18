from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True) 
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set', 
        blank=True,
    )

    # Override the user_permissions field
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set', 
        blank=True,
    )
    def __str__(self):
        return self.first_name + self.last_name
    
class Article(models.Model):
    source = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.TextField()
    url_to_image = models.TextField(blank=True, null=True)
    published_at = models.DateField(_("Published Date"))
    # content = models.TextField()
    category = models.CharField(max_length=255)
    full_content = models.TextField()
    transferred = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.article.title}"

class Review(models.Model):
    class Rating(models.IntegerChoices):
        ONE = 1, '1 - Very Poor'
        TWO = 2, '2 - Poor'
        THREE = 3, '3 - Average'
        FOUR = 4, '4 - Good'
        FIVE = 5, '5 - Excellent'
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=Rating.choices)
    feedback = models.TextField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.rating}"
    

class UserActivityLogs(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    




