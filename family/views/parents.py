from rest_framework import viewsets
from family.models import ParentChild
from family.serializers import (
    ParentChildSerializer
)


class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer
