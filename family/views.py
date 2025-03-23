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
    queryset = Person.objects.all().order_by('generation_level')
    serializer_class = PersonSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'generation_level']
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        
        if search_query:
            # Tìm người theo tên
            searched_person = queryset.filter(name__icontains=search_query).first()
            if searched_person:
                # Lấy tất cả cha mẹ của người này
                parents = []
                current = searched_person
                while True:
                    parent_relations = current.parent_relations.all()
                    if not parent_relations:
                        break
                    parent = parent_relations[0].parent
                    parents.append(parent.id)
                    current = parent

                # Chỉ trả về expanded=True trong response mà không cập nhật database
                queryset = queryset.all()
                for person in queryset:
                    if person.id in parents or person.id == searched_person.id:
                        person.expanded = True

        return queryset

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
