from rest_framework import viewsets
from family.models import Marriage
from family.serializers import (
    MarriageSerializer
)


class MarriageViewSet(viewsets.ModelViewSet):
    queryset = Marriage.objects.all()
    serializer_class = MarriageSerializer
