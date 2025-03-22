from django.contrib import admin
from .models import Person, Marriage, ParentChild, Sibling


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 'generation_level', 'expanded', 'description', 'image_url')
    search_fields = ('name', 'id')
    list_filter = ('gender', 'generation_level')


@admin.register(Marriage)
class MarriageAdmin(admin.ModelAdmin):
    list_display = ('spouse1', 'spouse2', 'marriage_type', 'marriage_date')
    list_filter = ('marriage_type',)


@admin.register(ParentChild)
class ParentChildAdmin(admin.ModelAdmin):
    list_display = ('parent', 'child', 'relationship_type')
    list_filter = ('relationship_type',)


@admin.register(Sibling)
class SiblingAdmin(admin.ModelAdmin):
    list_display = ('person1', 'person2', 'relationship_type')
    list_filter = ('relationship_type',) 