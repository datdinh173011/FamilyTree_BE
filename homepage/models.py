from django.db import models


class Homepage(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    # List of images
    images = models.JSONField(verbose_name="Danh sách ảnh", default=list)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Ngày cập nhật")
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái")

    class Meta:
        verbose_name = "Trang chủ"
        verbose_name_plural = "Trang chủ"
        ordering = ['-created_at']
