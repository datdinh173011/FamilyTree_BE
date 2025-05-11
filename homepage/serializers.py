from rest_framework import serializers
from .models import Homepage


class HomepageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Homepage model.
    """
    class Meta:
        model = Homepage
        fields = [
            'id', 'title', 'content', 'images',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
