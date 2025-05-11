from django.urls import path, include
from rest_framework.routers import DefaultRouter
from family.views import (
    PersonViewSet, MarriageViewSet, ParentChildViewSet, SiblingViewSet
)

router = DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'marriages', MarriageViewSet)
router.register(r'parent-child', ParentChildViewSet)
router.register(r'siblings', SiblingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
