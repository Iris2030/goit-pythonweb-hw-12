from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from models import Base, Student, Group, Teacher, Subject, Grade
import random
from datetime import datetime

engine = create_engine('postgresql://postgres:12345@localhost:5434/postgres')
Session = sessionmaker(bind=engine)
session = Session()

faker = Faker()

groups = [Group(name=faker.word()) for _ in range(3)]
session.add_all(groups)

teachers = [Teacher(name=faker.name()) for _ in range(3)]
session.add_all(teachers)

subjects = [Subject(name=faker.word(), teacher=random.choice(teachers)) for _ in range(5)]
session.add_all(subjects)

students = [Student(name=faker.name(), group=random.choice(groups)) for _ in range(50)]
session.add_all(students)

for student in students:
    for subject in subjects:
        for _ in range(random.randint(1, 5)):  # до 5 оцінок для кожного студента
            grade = Grade(
                student=student,
                subject=subject,
                grade=random.uniform(60, 100),
                date_received=faker.date_between(start_date='-1y', end_date='today')
            )
            session.add(grade)

session.commit()
