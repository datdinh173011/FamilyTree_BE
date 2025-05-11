from rest_framework.permissions import AllowAny
from django.db import transaction
from datetime import datetime
from django_filters import rest_framework as filters
from family.models import Person, Marriage, ParentChild, Sibling
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from family.serializers import (
    PersonSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404


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
            searched_person = queryset.filter(
                name__icontains=search_query).first()
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
                        marriages = list(parent.marriages_as_spouse1.all(
                        )) + list(parent.marriages_as_spouse2.all())
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
                marriages = list(searched_person.marriages_as_spouse1.all(
                )) + list(searched_person.marriages_as_spouse2.all())
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

        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.get_queryset()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @action(detail=False, methods=['get'])
    def family_tree(self, request):
        persons = self.get_queryset()
        serializer = self.get_serializer(persons, many=True)
        return Response({"products": serializer.data})

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            parent_id = request.data.get('parent_id')
            spouse_id = request.data.get('spouse_id')
            date_of_birth = None
            date_of_death = None
            date_str = request.data.get('date_of_birth')
            if date_str:
                date_of_birth = datetime.strptime(date_str, '%Y-%m-%d').date()
            date_str = request.data.get('date_of_death')
            if date_str:
                date_of_death = datetime.strptime(date_str, '%Y-%m-%d').date()

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_person = serializer.save()
            # Now set the date fields after the object is created
            if date_of_birth:
                new_person.date_of_birth = date_of_birth
            if date_of_death:
                new_person.date_of_death = date_of_death
            new_person.save()

            if parent_id:
                # Create parent-child relationships
                try:
                    parent = Person.objects.get(id=parent_id)
                    ParentChild.objects.create(parent=parent, child=new_person)
                    # Create sibling relationships
                    siblings = list(parent.sibling_relations1.all()) + \
                        list(parent.sibling_relations2.all())
                    for sibling in siblings:
                        if sibling.person1_id != parent.id:
                            Sibling.objects.create(
                                person1=new_person, person2=sibling.person1)
                        if sibling.person2_id != parent.id:
                            Sibling.objects.create(
                                person1=new_person, person2=sibling.person2)

                except Person.DoesNotExist:
                    return Response(
                        {"error": "Parent not found"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif spouse_id:
                # Create marriage relationship
                try:
                    spouse = Person.objects.get(id=spouse_id)
                    Marriage.objects.create(
                        spouse1=new_person, spouse2=spouse)
                except Person.DoesNotExist:
                    return Response(
                        {"error": "Spouse not found"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
