from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'persons', views.PersonViewSet)
router.register(r'marriages', views.MarriageViewSet)
router.register(r'parent-child', views.ParentChildViewSet)
router.register(r'siblings', views.SiblingViewSet)

app_name = 'family'

urlpatterns = [
    path('api/', include(router.urls)),
]