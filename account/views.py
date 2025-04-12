from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

# JWT imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .models.users import User
from .serializers import UserSerializer, UserDetailSerializer


class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication view that handles user login
    and returns a token along with user details
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Update last activity
        user.last_activity = timezone.now()
        user.save()
        
        # Return token and user details
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that returns more user details
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # Get the user for additional info
        username = request.data.get('username')
        user = User.objects.get(username=username)
        
        # Update last activity
        user.last_activity = timezone.now()
        user.save()
        
        # Add user details to response
        response_data = serializer.validated_data
        user_serializer = UserSerializer(user)
        response_data['user'] = user_serializer.data
        
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout - deletes the user's auth token and blacklists JWT
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Handle Token logout
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            
            # Handle JWT logout
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing user accounts
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Handle user registration"""
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()
    
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
