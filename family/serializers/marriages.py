from rest_framework import serializers
from family.models import Marriage


class MarriageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marriage
        fields = [
            'id', 'spouse1', 'spouse2', 'marriage_type', 'marriage_date'
        ]
