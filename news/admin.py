from django.contrib import admin
from .models import NewsCategory, NewsArticle, NewsComment

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'published_at', 'view_count', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
    list_filter = ('article',)
    search_fields = ('content',)
