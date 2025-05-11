from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomepageViewSet

router = DefaultRouter()
router.register('', HomepageViewSet, basename='homepage')

urlpatterns = [
    path('', include(router.urls)),
]
