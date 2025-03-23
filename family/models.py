from django.db import models

class Person(models.Model):
    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Họ tên")
    gender = models.CharField(
        max_length=10, 
        choices=GENDER_CHOICES,
        verbose_name="Giới tính"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="URL ảnh")
    image = models.URLField(blank=True, null=True, verbose_name="Ảnh")
    expanded = models.BooleanField(default=False)
    generation_level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_spouses(self):
        spouses = []
        # Lấy các cuộc hôn nhân với vai trò là spouse1
        marriages1 = self.marriages_as_spouse1.all()
        for marriage in marriages1:
            spouses.append({
                "id": marriage.spouse2.id,
                "type": marriage.marriage_type
            })
        
        # Lấy các cuộc hôn nhân với vai trò là spouse2
        marriages2 = self.marriages_as_spouse2.all()
        for marriage in marriages2:
            spouses.append({
                "id": marriage.spouse1.id,
                "type": marriage.marriage_type
            })
        return spouses

    def get_children(self):
        children = []
        for relation in self.children_relations.all():
            children.append({
                "id": relation.child.id,
                "type": relation.relationship_type
            })
        return children

    class Meta:
        verbose_name = "Thành viên"
        verbose_name_plural = "Thành viên"


class Marriage(models.Model):
    MARRIAGE_TYPES = [
        ('married', 'Đã kết hôn'),
        ('divorced', 'Đã ly hôn'),
    ]

    spouse1 = models.ForeignKey(
        Person, 
        on_delete=models.CASCADE,
        related_name='marriages_as_spouse1'
    )
    spouse2 = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='marriages_as_spouse2'
    )
    marriage_type = models.CharField(
        max_length=20,
        choices=MARRIAGE_TYPES,
        default='married'
    )
    marriage_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.spouse1.name} - {self.spouse2.name}"

    class Meta:
        verbose_name = "Hôn nhân"
        verbose_name_plural = "Hôn nhân"


class ParentChild(models.Model):
    RELATIONSHIP_TYPES = [
        ('blood', 'Con đẻ'),
        ('adopted', 'Con nuôi'),
    ]

    parent = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='children_relations'
    )
    child = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='parent_relations'
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        default='blood'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent.name} - {self.child.name}"

    class Meta:
        verbose_name = "Quan hệ cha mẹ - con"
        verbose_name_plural = "Quan hệ cha mẹ - con"


class Sibling(models.Model):
    SIBLING_TYPES = [
        ('blood', 'Anh chị em ruột'),
        ('half', 'Anh chị em cùng cha/mẹ'),
        ('step', 'Anh chị em kết'),
    ]

    person1 = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='sibling_relations1'
    )
    person2 = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='sibling_relations2'
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=SIBLING_TYPES,
        default='blood'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.person1.name} - {self.person2.name}"

    class Meta:
        verbose_name = "Quan hệ anh chị em"
        verbose_name_plural = "Quan hệ anh chị em" 