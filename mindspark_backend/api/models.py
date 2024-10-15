from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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

    




