from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import NewsCategory, NewsArticle, NewsComment
from .serializers import (
    NewsCategorySerializer,
    NewsArticleSerializer,
    NewsArticleDetailSerializer,
    NewsCommentSerializer
)


class NewsCategoryViewSet(viewsets.ModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_published']
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsArticleDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.is_published = True
        article.published_at = timezone.now()
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        article = self.get_object()
        article.is_published = False
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)


class NewsCommentViewSet(viewsets.ModelViewSet):
    queryset = NewsComment.objects.all().order_by('-created_at')
    serializer_class = NewsCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['article', 'user']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
