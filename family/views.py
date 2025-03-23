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
                # Danh sách ID cần expanded
                expand_ids = set()
                
                # Thêm người được tìm thấy
                expand_ids.add(searched_person.id)
                
                # Lấy tất cả cha mẹ và tổ tiên
                current = searched_person
                while True:
                    parent_relations = current.parent_relations.all()
                    if not parent_relations:
                        break
                    for relation in parent_relations:
                        parent = relation.parent
                        expand_ids.add(parent.id)
                        
                        # Thêm vợ/chồng của parent
                        marriages = list(parent.marriages_as_spouse1.all()) + list(parent.marriages_as_spouse2.all())
                        for marriage in marriages:
                            if marriage.spouse1_id != parent.id:
                                expand_ids.add(marriage.spouse1_id)
                            if marriage.spouse2_id != parent.id:
                                expand_ids.add(marriage.spouse2_id)
                        
                        # Thêm anh chị em của parent
                        siblings1 = parent.sibling_relations1.all()
                        siblings2 = parent.sibling_relations2.all()
                        for sibling in siblings1:
                            expand_ids.add(sibling.person2_id)
                        for sibling in siblings2:
                            expand_ids.add(sibling.person1_id)
                    
                    # Chuyển lên parent tiếp theo
                    current = parent_relations[0].parent

                # Lấy vợ/chồng của người được tìm thấy
                marriages = list(searched_person.marriages_as_spouse1.all()) + list(searched_person.marriages_as_spouse2.all())
                for marriage in marriages:
                    if marriage.spouse1_id != searched_person.id:
                        expand_ids.add(marriage.spouse1_id)
                    if marriage.spouse2_id != searched_person.id:
                        expand_ids.add(marriage.spouse2_id)

                # Lấy anh chị em của người được tìm thấy
                siblings1 = searched_person.sibling_relations1.all()
                siblings2 = searched_person.sibling_relations2.all()
                for sibling in siblings1:
                    expand_ids.add(sibling.person2_id)
                for sibling in siblings2:
                    expand_ids.add(sibling.person1_id)

                # Set expanded=True cho tất cả ID đã thu thập
                queryset = queryset.all()
                for person in queryset:
                    if person.id in expand_ids:
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
