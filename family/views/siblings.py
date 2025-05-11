from family.models import Sibling
from rest_framework import viewsets
from family.serializers import (
    SiblingSerializer
)


class SiblingViewSet(viewsets.ModelViewSet):
    queryset = Sibling.objects.all()
    serializer_class = SiblingSerializer
