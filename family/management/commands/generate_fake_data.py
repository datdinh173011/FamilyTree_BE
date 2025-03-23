from django.core.management.base import BaseCommand
from family.models import Person, Marriage, ParentChild, Sibling
from faker import Faker
import random
from datetime import datetime, timedelta, date

fake = Faker(['vi_VN'])

class Command(BaseCommand):
    help = 'Tạo dữ liệu giả cho family tree với 6 thế hệ, khoảng 100 người'

    def generate_random_date(self, year):
        """Helper function để tạo ngày ngẫu nhiên trong năm"""
        month = random.randint(1, 12)
        # Xác định số ngày trong tháng
        if month in [4, 6, 9, 11]:
            max_day = 30
        elif month == 2:
            # Xử lý năm nhuận
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        else:
            max_day = 31
        
        day = random.randint(1, max_day)
        return date(year, month, day)

    def generate_person(self, gender, generation):
        """Tạo một người với giới tính và thế hệ xác định"""
        if gender == 'male':
            name = fake.name_male()
        else:
            name = fake.name_female()
        
        # Tính năm sinh dựa vào thế hệ
        current_year = datetime.now().year
        if generation == 1:
            year_of_birth = random.randint(1950, 1960)
        elif generation == 2:
            year_of_birth = random.randint(1970, 1980)
        elif generation == 3:
            year_of_birth = random.randint(1985, 1995)
        elif generation == 4:
            year_of_birth = random.randint(2000, 2010)
        elif generation == 5:
            year_of_birth = random.randint(2010, 2015)
        else:
            year_of_birth = random.randint(2015, 2020)
        
        # Tạo ngày sinh
        date_of_birth = self.generate_random_date(year_of_birth)
        
        # Xác định xem người này còn sống hay đã mất
        is_deceased = False
        if generation == 1:
            is_deceased = random.random() < 0.7
        elif generation == 2:
            is_deceased = random.random() < 0.3
        elif generation == 3:
            is_deceased = random.random() < 0.1
        
        # Nếu đã mất, tạo ngày mất và năm mất
        date_of_death = None
        year_of_death = None
        if is_deceased:
            min_age = 50 if generation <= 2 else 40
            max_age = 80 if generation <= 2 else 70
            year_of_death = min(current_year, year_of_birth + random.randint(min_age, max_age))
            date_of_death = self.generate_random_date(year_of_death)
        
        # Xác định thứ bậc trong gia đình
        family_rank_choices = ['Trưởng', 'Thứ', 'Út']
        family_rank = random.choice(family_rank_choices)
        
        # Tạo địa chỉ
        permanent_address = f"{fake.street_address()}, {fake.city()}"
            
        return Person.objects.create(
            name=name,
            gender=gender,
            date_of_birth=date_of_birth,
            year_of_birth=year_of_birth,
            date_of_death=date_of_death,
            year_of_death=year_of_death,
            family_rank=family_rank,
            generation_level=generation,
            permanent_address=permanent_address,
            description=fake.text(max_nb_chars=200),
            image_url=f"https://picsum.photos/id/{random.randint(1, 1000)}/200/200",
            expanded=generation <= 2,
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
        
        # Tạo hôn nhân với ngày cưới sau ngày sinh của cả hai người
        earliest_marriage_date = max(husband.date_of_birth, wife.date_of_birth)
        marriage_year = earliest_marriage_date.year + random.randint(18, 25)
        marriage_date = self.generate_random_date(marriage_year)
        
        marriage = Marriage.objects.create(
            spouse1=husband,
            spouse2=wife,
            marriage_type='married',
            marriage_date=marriage_date
        )
        
        # Điều chỉnh số con dựa vào thế hệ
        if generation == 1:
            num_children = random.randint(4, 5)  # Thế hệ 1: 4-5 con
        elif generation == 2:
            num_children = random.randint(3, 4)  # Thế hệ 2: 3-4 con
        elif generation == 3:
            num_children = random.randint(3, 4)  # Thế hệ 3: 3-4 con
        elif generation == 4:
            num_children = random.randint(2, 3)  # Thế hệ 4: 2-3 con
        elif generation == 5:
            num_children = random.randint(1, 2)  # Thế hệ 5: 1-2 con
        else:
            num_children = 1  # Thế hệ 6: 1 con
        
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
        
        # Tạo các thế hệ tiếp theo (2-6)
        for generation in range(2, 7):
            self.stdout.write(f'Đang tạo thế hệ {generation}...')
            next_generation = []
            next_parent_map = {}
            
            for person in current_generation:
                # Điều chỉnh xác suất có con theo thế hệ
                if generation == 2:
                    chance = 0.95  # 95% cơ hội có con ở thế hệ 2
                elif generation == 3:
                    chance = 0.90  # 90% cơ hội có con ở thế hệ 3
                elif generation == 4:
                    chance = 0.85  # 85% cơ hội có con ở thế hệ 4
                elif generation == 5:
                    chance = 0.80  # 80% cơ hội có con ở thế hệ 5
                else:
                    chance = 0.70  # 70% cơ hội có con ở thế hệ 6
                
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
        for gen in range(1, 7):
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