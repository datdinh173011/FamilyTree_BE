from rest_framework import serializers
from family.models import ParentChild


class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = ['id', 'parent', 'child', 'relationship_type']
