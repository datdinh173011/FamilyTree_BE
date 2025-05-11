from rest_framework import serializers
from .models import UploadedFile
from account.serializers import UserSerializer
import magic
import os


class UploadedFileSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'file_url', 'file_type', 'title', 'description',
                  'uploaded_by', 'created_at', 'updated_at', 'filename',
                  'file_extension', 'file_size', 'mime_type']
        read_only_fields = ['uploaded_by',
                            'file_url', 'file_size', 'mime_type']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request is not None:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_file_size(self, obj):
        if obj.file and hasattr(obj.file, 'size'):
            size = obj.file.size
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024 or unit == 'TB':
                    return f"{size:.2f} {unit}"
                size /= 1024
        return "0 B"

    def get_mime_type(self, obj):
        if obj.file and hasattr(obj.file, 'path') and os.path.exists(obj.file.path):
            try:
                mime = magic.Magic(mime=True)
                return mime.from_file(obj.file.path)
            except Exception:
                pass
        return None

    def create(self, validated_data):
        """Set the uploaded_by field to the current user"""
        validated_data['uploaded_by'] = self.context['request'].user

        # Automatically determine file type based on extension
        file = validated_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
                validated_data['file_type'] = 'image'
            elif ext == '.pdf':
                validated_data['file_type'] = 'pdf'
            elif ext in ['.doc', '.docx', '.txt', '.rtf', '.odt', '.xlsx', '.csv']:
                validated_data['file_type'] = 'document'
            elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm']:
                validated_data['file_type'] = 'video'
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                validated_data['file_type'] = 'audio'
            else:
                validated_data['file_type'] = 'other'

        return super().create(validated_data)
