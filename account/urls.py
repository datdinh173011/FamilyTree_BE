from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    CustomAuthToken, 
    LogoutView, 
    UserViewSet,
    CustomTokenObtainPairView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Traditional token authentication
    path('login/token/', CustomAuthToken.as_view(), name='api_token_login'),
    # JWT authentication
    path('login/jwt/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Logout
    path('logout/', LogoutView.as_view(), name='api_logout'),
    # User profile
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user_me'),
    # Password management
    path('password/reset/', UserViewSet.as_view({'post': 'request_password_reset'}), name='password_reset_request'),
    path('password/reset/confirm/', UserViewSet.as_view({'post': 'reset_password_confirm'}), name='password_reset_confirm'),
    path('password/change/', UserViewSet.as_view({'post': 'change_password'}), name='password_change'),
]
