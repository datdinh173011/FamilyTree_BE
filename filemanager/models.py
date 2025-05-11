from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models.users import User
import os


def user_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.uploaded_by.id}/{filename}'


class UploadedFile(models.Model):
    FILE_TYPES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    file = models.FileField(
        upload_to=user_directory_path, verbose_name=_("File"))
    file_type = models.CharField(
        max_length=20, choices=FILE_TYPES, verbose_name=_("File Type"))
    title = models.CharField(
        max_length=255, blank=True, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name=_("Uploaded By"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

    @property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0

    def __str__(self):
        return self.title or self.filename

    class Meta:
        verbose_name = _("Uploaded File")
        verbose_name_plural = _("Uploaded Files")
