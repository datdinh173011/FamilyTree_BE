from django.core.management.base import BaseCommand
from family.models import Person, Marriage, ParentChild, Sibling
from faker import Faker
import random
from datetime import datetime, timedelta, date

fake = Faker(['vi_VN'])


class Command(BaseCommand):
    help = 'Tạo dữ liệu giả cho family tree với khoảng 100 người'

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

        # Điều chỉnh năm sinh theo thế hệ
        current_year = datetime.now().year
        birth_year_ranges = {
            1: (1940, 1950),   # Thế hệ 1: 1940-1950
            2: (1960, 1970),   # Thế hệ 2: 1960-1970
            3: (1980, 1990),   # Thế hệ 3: 1980-1990
            4: (2000, 2010),   # Thế hệ 4: 2000-2010
            5: (2010, 2020),   # Thế hệ 5: 2010-2020
        }

        # Sử dụng mặc định cho các thế hệ không xác định
        start_year, end_year = birth_year_ranges.get(generation, (2015, 2023))
        year_of_birth = random.randint(start_year, end_year)

        # Tạo ngày sinh
        date_of_birth = self.generate_random_date(year_of_birth)

        # Xác định xem người này còn sống hay đã mất
        is_deceased = False
        if generation == 1:
            is_deceased = random.random() < 0.6  # 60% thế hệ 1 đã mất
        elif generation == 2:
            is_deceased = random.random() < 0.2  # 20% thế hệ 2 đã mất

        # Nếu đã mất, tạo ngày mất
        date_of_death = None
        if is_deceased:
            min_age = 50 if generation <= 2 else 40
            max_age = 80 if generation <= 2 else 70
            year_of_death = min(
                current_year, year_of_birth + random.randint(min_age, max_age)
            )
            date_of_death = self.generate_random_date(year_of_death)

        # Xác định thứ bậc trong gia đình
        family_rank_choices = ['1', '2', '3', '4', '5', 'other']
        family_rank = random.choice(family_rank_choices)

        # Tạo địa chỉ
        permanent_address = f"{fake.street_address()}, {fake.city()}"

        return Person.objects.create(
            name=name,
            gender=gender,
            date_of_birth=date_of_birth,
            date_of_death=date_of_death,
            family_rank=family_rank,
            generation_level=generation,
            permanent_address=permanent_address,
            description=fake.text(max_nb_chars=200),
            expanded=generation < 3,
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

        # Điều chỉnh số con dựa vào thế hệ để đạt được khoảng 100 người
        child_count = {
            1: (3, 5),    # Thế hệ 1: 3-5 con
            2: (2, 4),    # Thế hệ 2: 2-4 con
            3: (1, 3),    # Thế hệ 3: 1-3 con
            4: (0, 2),    # Thế hệ 4: 0-2 con
        }

        min_children, max_children = child_count.get(generation, (0, 1))
        num_children = random.randint(min_children, max_children)

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
        Marriage.objects.all().delete()
        ParentChild.objects.all().delete()
        Sibling.objects.all().delete()

        # Tạo thế hệ đầu tiên - bắt đầu với một gia đình gốc
        self.stdout.write('Đang tạo thế hệ 1...')
        current_generation, parent_ids = self.create_family_unit(1)
        parent_map = {child.id: parent_ids for child in current_generation}

        # Tạo các thế hệ tiếp theo (2-5)
        max_persons = 100  # Giới hạn tổng số người
        total_persons = 2  # Bắt đầu với 2 người (cặp vợ chồng gốc)

        for generation in range(2, 6):
            self.stdout.write(f'Đang tạo thế hệ {generation}...')
            next_generation = []
            next_parent_map = {}

            # Kiểm tra số người hiện tại
            total_persons = Person.objects.count()
            if total_persons >= max_persons:
                self.stdout.write(
                    f'Đã đạt giới hạn {max_persons} người, dừng tạo dữ liệu.')
                break

            # Những người trong thế hệ hiện tại có thể kết hôn và có con
            for person in current_generation:
                # Chỉ tạo gia đình mới nếu chưa đạt đến giới hạn số người
                if total_persons < max_persons and random.random() < 0.85:  # 85% khả năng có gia đình
                    children, new_parent_ids = self.create_family_unit(
                        generation,
                        parent_map.get(person.id)
                    )
                    next_generation.extend(children)
                    for child in children:
                        next_parent_map[child.id] = new_parent_ids
                    # Cập nhật số người hiện tại
                    total_persons = Person.objects.count()

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
        for gen in range(1, 6):
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
