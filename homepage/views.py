from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Homepage
from .serializers import HomepageSerializer


class HomepageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing homepage instances.
    """
    queryset = Homepage.objects.all().order_by('-created_at')
    serializer_class = HomepageSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        # For listing, we can optionally filter by is_active
        queryset = self.queryset
        if request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Get a single homepage instance by ID.
        """
        homepage = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(homepage)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new homepage instance.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update an existing homepage instance.
        """
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        Partially update a homepage instance.
        """
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Delete a homepage instance.
        """
        instance = get_object_or_404(self.queryset, pk=pk)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
