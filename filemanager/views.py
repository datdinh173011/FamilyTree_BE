from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import UploadedFile
from .serializers import UploadedFileSerializer
import os

class UploadedFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing file uploads
    """
    queryset = UploadedFile.objects.all().order_by('-created_at')
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file_type', 'uploaded_by']
    search_fields = ['title', 'description', 'file']
    ordering_fields = ['created_at', 'updated_at', 'title']
    
    def get_queryset(self):
        """Filter files to only show user's own files unless staff"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Staff can see all files
        if user.is_staff:
            return queryset
        
        # Regular users can only see their own files
        return queryset.filter(uploaded_by=user)
    
    def perform_create(self, serializer):
        """Set the uploaded_by field to the current user"""
        serializer.save(uploaded_by=self.request.user)
        
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Upload multiple files at once
        """
        files = request.FILES.getlist('files')
        if not files:
            return Response(
                {"error": "No files were provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        uploaded_files = []
        errors = []
        
        for file in files:
            data = {
                'file': file,
                'file_type': request.data.get('file_type', 'other'),
                'title': request.data.get('title', ''),
                'description': request.data.get('description', '')
            }
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(uploaded_by=request.user)
                uploaded_files.append(serializer.data)
            else:
                errors.append({
                    'filename': file.name,
                    'errors': serializer.errors
                })
        
        return Response({
            'uploaded_files': uploaded_files,
            'errors': errors,
            'success_count': len(uploaded_files),
            'error_count': len(errors)
        }, status=status.HTTP_201_CREATED if uploaded_files else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Delete multiple files at once
        """
        file_ids = request.data.get('file_ids', [])
        if not file_ids:
            return Response(
                {"error": "No file IDs were provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = request.user
        deleted_count = 0
        not_found = []
        
        for file_id in file_ids:
            try:
                file_obj = UploadedFile.objects.get(id=file_id)
                
                # Check if user has permission to delete this file
                if user.is_staff or file_obj.uploaded_by == user:
                    file_obj.delete()
                    deleted_count += 1
                else:
                    not_found.append(file_id)
            except UploadedFile.DoesNotExist:
                not_found.append(file_id)
        
        return Response({
            'deleted_count': deleted_count,
            'not_found': not_found
        }, status=status.HTTP_200_OK)
