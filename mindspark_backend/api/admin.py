from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Article)
admin.site.register(Bookmark)
admin.site.register(Review)
admin.site.register(UserActivityLogs)
