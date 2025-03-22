from rest_framework import serializers
from .models import Person, Marriage, ParentChild, Sibling

class MarriageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marriage
        fields = ['id', 'spouse1', 'spouse2', 'marriage_type', 'marriage_date']

class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = ['id', 'parent', 'child', 'relationship_type']

class SiblingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sibling
        fields = ['id', 'person1', 'person2', 'relationship_type']

class PersonSerializer(serializers.ModelSerializer):
    spouses = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    parents = serializers.SerializerMethodField()
    siblings = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'name', 'gender', 'image', 'expanded', 
                 'generation_level', 'spouses', 'children', 
                 'parents', 'siblings']

    def get_spouses(self, obj):
        spouses = []
        marriages1 = obj.marriages_as_spouse1.all()
        marriages2 = obj.marriages_as_spouse2.all()

        for marriage in marriages1:
            spouses.append({
                "id": marriage.spouse2.id,
                "type": marriage.marriage_type
            })
        
        for marriage in marriages2:
            spouses.append({
                "id": marriage.spouse1.id,
                "type": marriage.marriage_type
            })
        return spouses

    def get_children(self, obj):
        return [{
            "id": relation.child.id,
            "type": relation.relationship_type
        } for relation in obj.children_relations.all()]

    def get_parents(self, obj):
        return [{
            "id": relation.parent.id,
            "type": relation.relationship_type
        } for relation in obj.parent_relations.all()]

    def get_siblings(self, obj):
        siblings = []
        sibling_relations1 = obj.sibling_relations1.all()
        sibling_relations2 = obj.sibling_relations2.all()

        for relation in sibling_relations1:
            siblings.append({
                "id": relation.person2.id,
                "type": relation.relationship_type
            })
        
        for relation in sibling_relations2:
            siblings.append({
                "id": relation.person1.id,
                "type": relation.relationship_type
            })
        return siblings 