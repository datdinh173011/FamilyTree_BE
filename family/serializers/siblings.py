from rest_framework import serializers
from family.models import Sibling


class SiblingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sibling
        fields = ['id', 'person1', 'person2', 'relationship_type']
