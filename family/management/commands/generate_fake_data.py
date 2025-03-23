from django.core.management.base import BaseCommand
from family.models import Person, Marriage, ParentChild, Sibling
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker(['vi_VN'])

class Command(BaseCommand):
    help = 'Tạo dữ liệu giả cho family tree với 10 thế hệ'

    def generate_person(self, gender, generation):
        """Tạo một người với giới tính và thế hệ xác định"""
        if gender == 'male':
            name = fake.name_male()
        else:
            name = fake.name_female()
            
        return Person.objects.create(
            name=name,
            gender=gender,
            description=fake.text(max_nb_chars=200),
            image_url=f"https://picsum.photos/id/{random.randint(1, 1000)}/200/200",
            expanded=False,
            generation_level=generation
        )

    def create_family_unit(self, generation):
        """Tạo một đơn vị gia đình (vợ chồng và con cái)"""
        # Tạo chồng và vợ
        husband = self.generate_person('male', generation)
        wife = self.generate_person('female', generation)
        
        # Tạo hôn nhân
        marriage = Marriage.objects.create(
            spouse1=husband,
            spouse2=wife,
            marriage_type='married',
            marriage_date=fake.date_between(
                start_date='-60y',
                end_date='-20y'
            )
        )
        
        # Tạo con cái (2-5 người con)
        children = []
        num_children = random.randint(2, 5)
        for _ in range(num_children):
            gender = random.choice(['male', 'female'])
            child = self.generate_person(gender, generation + 1)
            children.append(child)
            
            # Tạo quan hệ cha mẹ - con
            ParentChild.objects.create(
                parent=husband,
                child=child,
                relationship_type='blood'
            )
            ParentChild.objects.create(
                parent=wife,
                child=child,
                relationship_type='blood'
            )
        
        # Tạo quan hệ anh chị em giữa các con
        for i in range(len(children)):
            for j in range(i + 1, len(children)):
                Sibling.objects.create(
                    person1=children[i],
                    person2=children[j],
                    relationship_type='blood'
                )
        
        return children

    def handle(self, *args, **kwargs):
        # Xóa dữ liệu cũ
        self.stdout.write('Đang xóa dữ liệu cũ...')
        Person.objects.all().delete()
        
        # Tạo thế hệ đầu tiên
        self.stdout.write('Đang tạo thế hệ 1...')
        current_generation = self.create_family_unit(1)
        
        # Tạo các thế hệ tiếp theo
        for generation in range(2, 11):
            self.stdout.write(f'Đang tạo thế hệ {generation}...')
            next_generation = []
            
            # Với mỗi người trong thế hệ hiện tại
            for person in current_generation:
                # 70% khả năng người này sẽ lập gia đình và có con
                if random.random() < 0.7:
                    children = self.create_family_unit(generation)
                    next_generation.extend(children)
            
            current_generation = next_generation
            if not current_generation:
                break
        
        # Thống kê kết quả
        total_persons = Person.objects.count()
        total_marriages = Marriage.objects.count()
        total_parent_child = ParentChild.objects.count()
        total_siblings = Sibling.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'''
        Đã tạo xong dữ liệu giả:
        - Tổng số người: {total_persons}
        - Tổng số cuộc hôn nhân: {total_marriages}
        - Tổng số quan hệ cha mẹ - con: {total_parent_child}
        - Tổng số quan hệ anh chị em: {total_siblings}
        ''')) 