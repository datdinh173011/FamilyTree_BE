from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsCategoryViewSet, NewsArticleViewSet, NewsCommentViewSet

router = DefaultRouter()
router.register('categories', NewsCategoryViewSet)
router.register('articles', NewsArticleViewSet)
router.register('comments', NewsCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
