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
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser


class PersonViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Person.objects.all().order_by('generation_level')
    serializer_class = PersonSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'generation_level']
    search_fields = ['name']
    parser_classes = [MultiPartParser, FormParser]

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
        
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add_family_member(self, request):
        """Add a new family member with relationships"""
        # Extract data from request
        data = request.data
        
        # Validate required fields
        required_fields = ['name', 'gender', 'generation_level']
        for field in required_fields:
            if field not in data or not data[field]:
                return Response(
                    {"error": f"Field '{field}' is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create new person
        person_data = {
            'name': data.get('name'),
            'gender': data.get('gender'),
            'generation_level': data.get('generation_level'),
            'date_of_birth': data.get('birth_year'),
            'date_of_death': data.get('death_year'),
            'family_rank': data.get('role', ''),
            'permanent_address': data.get('address', ''),
            'description': data.get('biography', '')
        }
        
        # Handle photo if provided
        if 'photo' in request.FILES:
            person_data['image'] = request.FILES['photo']
            
        serializer = self.get_serializer(data=person_data)
        serializer.is_valid(raise_exception=True)
        new_person = serializer.save()
        
        # Create parent-child relationships
        if 'parent_id' in data and data['parent_id']:
            try:
                parent_id = int(data['parent_id'])
                parent = Person.objects.get(id=parent_id)
                ParentChild.objects.create(parent=parent, child=new_person)
            except (ValueError, Person.DoesNotExist):
                pass  # Ignore invalid parent IDs
        
        # Create marriage relationship
        if 'spouse_id' in data and data['spouse_id']:
            try:
                spouse_id = int(data['spouse_id'])
                spouse = Person.objects.get(id=spouse_id)
                # Determine which person should be spouse1 based on gender convention
                if new_person.gender == 'M':
                    spouse1, spouse2 = new_person, spouse
                else:
                    spouse1, spouse2 = spouse, new_person
                Marriage.objects.create(spouse1=spouse1, spouse2=spouse2)
            except (ValueError, Person.DoesNotExist):
                pass  # Ignore invalid spouse IDs
        
        # Create sibling relationships
        if 'sibling_ids' in data and data['sibling_ids']:
            sibling_ids = data.getlist('sibling_ids') if hasattr(data, 'getlist') else data['sibling_ids'].split(',')
            for sibling_id in sibling_ids:
                try:
                    sibling_id = int(sibling_id)
                    sibling = Person.objects.get(id=sibling_id)
                    # Ensure consistent ordering (lower ID is always person1)
                    if new_person.id < sibling.id:
                        Sibling.objects.create(person1=new_person, person2=sibling)
                    else:
                        Sibling.objects.create(person1=sibling, person2=new_person)
                except (ValueError, Person.DoesNotExist):
                    pass  # Ignore invalid sibling IDs
        
        # Create child relationships
        if 'child_ids' in data and data['child_ids']:
            child_ids = data.getlist('child_ids') if hasattr(data, 'getlist') else data['child_ids'].split(',')
            for child_id in child_ids:
                try:
                    child_id = int(child_id)
                    child = Person.objects.get(id=child_id)
                    ParentChild.objects.create(parent=new_person, child=child)
                except (ValueError, Person.DoesNotExist):
                    pass  # Ignore invalid child IDs
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarriageViewSet(viewsets.ModelViewSet):
    queryset = Marriage.objects.all()
    serializer_class = MarriageSerializer


class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer


class SiblingViewSet(viewsets.ModelViewSet):
    queryset = Sibling.objects.all()
    serializer_class = SiblingSerializer
