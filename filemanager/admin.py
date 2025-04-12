from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file_type', 'filename', 'uploaded_by', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('title', 'description', 'file')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
