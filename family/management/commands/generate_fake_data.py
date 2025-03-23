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

    def create_family_unit(self, generation, parent_ids=None):
        """
        Tạo một đơn vị gia đình (vợ chồng và con cái)
        parent_ids: tuple chứa (father_id, mother_id) nếu có
        """
        # Tạo chồng và vợ
        husband = self.generate_person('male', generation)
        wife = self.generate_person('female', generation)
        
        # Nếu có thông tin về cha mẹ, tạo quan hệ parent-child
        if parent_ids:
            father_id, mother_id = parent_ids
            if father_id:
                ParentChild.objects.create(
                    parent_id=father_id,
                    child=husband,
                    relationship_type='blood'
                )
            if mother_id:
                ParentChild.objects.create(
                    parent_id=mother_id,
                    child=husband,
                    relationship_type='blood'
                )
        
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
        
        # Tạo quan hệ anh chị em
        for i in range(len(children)):
            for j in range(i + 1, len(children)):
                Sibling.objects.create(
                    person1=children[i],
                    person2=children[j],
                    relationship_type='blood'
                )
        
        return children, (husband.id, wife.id)

    def handle(self, *args, **kwargs):
        # Xóa dữ liệu cũ
        self.stdout.write('Đang xóa dữ liệu cũ...')
        Person.objects.all().delete()
        
        # Tạo thế hệ đầu tiên
        self.stdout.write('Đang tạo thế hệ 1...')
        current_generation, parent_ids = self.create_family_unit(1)
        parent_map = {child.id: parent_ids for child in current_generation}
        
        # Tạo các thế hệ tiếp theo (2-4)
        for generation in range(2, 5):
            self.stdout.write(f'Đang tạo thế hệ {generation}...')
            next_generation = []
            next_parent_map = {}
            
            for person in current_generation:
                # Điều chỉnh xác suất có con theo thế hệ
                if generation == 2:
                    chance = 0.8  # 80% cơ hội có con ở thế hệ 2
                elif generation == 3:
                    chance = 0.6  # 60% cơ hội có con ở thế hệ 3
                else:
                    chance = 0.4  # 40% cơ hội có con ở thế hệ 4
                
                if random.random() < chance:
                    # Truyền thông tin cha mẹ khi tạo gia đình mới
                    children, new_parent_ids = self.create_family_unit(
                        generation, 
                        parent_map.get(person.id)
                    )
                    next_generation.extend(children)
                    # Lưu thông tin cha mẹ cho thế hệ tiếp theo
                    for child in children:
                        next_parent_map[child.id] = new_parent_ids
            
            current_generation = next_generation
            parent_map = next_parent_map
            
            if not current_generation:
                break
        
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