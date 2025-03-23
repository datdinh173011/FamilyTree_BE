from django.core.management.base import BaseCommand
from family.models import Person, Marriage, ParentChild, Sibling
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker(['vi_VN'])

class Command(BaseCommand):
    help = 'Tạo dữ liệu giả cho family tree với 4 thế hệ, khoảng 30 người'

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
            expanded=generation <= 2,  # 2 thế hệ đầu sẽ được mở rộng
            generation_level=generation
        )

    def create_family_unit(self, generation):
        """Tạo một đơn vị gia đình (vợ chồng và con cái)"""
        # Tạo chồng và vợ
        husband = self.generate_person('male', generation)
        wife = self.generate_person('female', generation)
        
        marriage = Marriage.objects.create(
            spouse1=husband,
            spouse2=wife,
            marriage_type='married',
            marriage_date=fake.date_between(
                start_date='-60y',
                end_date='-20y'
            )
        )
        
        # Điều chỉnh số con dựa vào thế hệ
        if generation == 1:
            num_children = 3  # Thế hệ 1 có 3 con
        elif generation == 2:
            num_children = 2  # Thế hệ 2 có 2 con
        elif generation == 3:
            num_children = random.randint(1, 2)  # Thế hệ 3 có 1-2 con
        else:
            num_children = 1  # Thế hệ 4 có 1 con
            
        children = []
        for _ in range(num_children):
            gender = random.choice(['male', 'female'])
            child = self.generate_person(gender, generation + 1)
            children.append(child)
            
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
        
        # Tạo quan hệ anh chị em
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
        
        # Tạo thế hệ đầu tiên (1 cặp vợ chồng)
        self.stdout.write('Đang tạo thế hệ 1...')
        current_generation = self.create_family_unit(1)
        
        # Tạo các thế hệ tiếp theo (2-4)
        for generation in range(2, 5):
            self.stdout.write(f'Đang tạo thế hệ {generation}...')
            next_generation = []
            
            for person in current_generation:
                # Điều chỉnh xác suất có con theo thế hệ
                if generation == 2:
                    chance = 0.8  # 80% cơ hội có con ở thế hệ 2
                elif generation == 3:
                    chance = 0.6  # 60% cơ hội có con ở thế hệ 3
                else:
                    chance = 0.4  # 40% cơ hội có con ở thế hệ 4
                
                if random.random() < chance:
                    children = self.create_family_unit(generation)
                    next_generation.extend(children)
            
            current_generation = next_generation
        
        # Thống kê kết quả
        total_persons = Person.objects.count()
        total_marriages = Marriage.objects.count()
        total_parent_child = ParentChild.objects.count()
        total_siblings = Sibling.objects.count()
        
        # Thống kê theo thế hệ
        generation_stats = {}
        for gen in range(1, 5):
            count = Person.objects.filter(generation_level=gen).count()
            generation_stats[gen] = count
        
        self.stdout.write(self.style.SUCCESS(f'''
        Đã tạo xong dữ liệu giả:
        - Tổng số người: {total_persons}
        - Tổng số cuộc hôn nhân: {total_marriages}
        - Tổng số quan hệ cha mẹ - con: {total_parent_child}
        - Tổng số quan hệ anh chị em: {total_siblings}
        
        Thống kê theo thế hệ:
        {chr(10).join(f"- Thế hệ {gen}: {count} người" for gen, count in generation_stats.items())}
        ''')) 