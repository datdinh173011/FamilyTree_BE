from rest_framework.permissions import AllowAny
from django_filters import rest_framework as filters
from family.models import Person, Marriage, ParentChild, Sibling
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    PersonSerializer, 
    MarriageSerializer,
    ParentChildSerializer,
    SiblingSerializer
)


class PersonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'generation_level']
    search_fields = ['name']

    @action(detail=False, methods=['get'])
    def family_tree(self, request):
        persons = self.get_queryset()
        serializer = self.get_serializer(persons, many=True)
        return Response({"products": serializer.data})


class MarriageViewSet(viewsets.ModelViewSet):
    queryset = Marriage.objects.all()
    serializer_class = MarriageSerializer


class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer


class SiblingViewSet(viewsets.ModelViewSet):
    queryset = Sibling.objects.all()
    serializer_class = SiblingSerializer
