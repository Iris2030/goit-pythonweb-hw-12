from connect import  session, close_session
from my_select import (
    select_1,
    select_2,
    select_3,
    select_4,
    select_5,
    select_6,
    select_7,
    select_8,
    select_9,
    select_10,
)

def test_queries():
    subject_id = 1
    teacher_id = 1
    group_id = 1
    student_id = 1

    try:
        # 1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів
        print("5 студентів із найбільшим середнім балом з усіх предметів:")
        for student, avg_grade in select_1():  
            print(f"{student}: {avg_grade:.2f}")
        print()

        # 2. Знайти студента із найвищим середнім балом з певного предмета
        print(f"Студент із найвищим середнім балом з предмета ID {subject_id}:")
        result = select_2(subject_id)   
        if result:
            student, avg_grade = result
            print(f"{student}: {avg_grade:.2f}")
        print()

        # 3. Знайти середній бал у групах з певного предмета
        print(f"Середній бал у групах з предмета ID {subject_id}:")
        for group_name, avg_grade in select_3(subject_id):   
            print(f"{group_name}: {avg_grade:.2f}")
        print()

        # 4. Знайти середній бал на потоці (по всій таблиці оцінок)
        print(f"Середній бал на потоці (по всій таблиці оцінок): {select_4():.2f}")  # Видалено session
        print()

        # 5. Знайти які курси читає певний викладач
        print(f"Які курси читає викладач з ID {teacher_id}:")
        for subject in select_5(teacher_id):  
            print(f"- {subject.name}")
        print()

        # 6. Знайти список студентів у певній групі
        print(f"Список студентів у групі з ID {group_id}:")
        for student in select_6(group_id):  
            print(f"- {student.name}")
        print()

        # 7. Знайти оцінки студентів у окремій групі з певного предмета
        print(f"Оцінки студентів у групі {group_id} з предмета {subject_id}:")
        for student, grade in select_7(group_id, subject_id):  
            print(f"{student.name}: {grade}")
        print()

        # 8. Знайти середній бал, який ставить певний викладач зі своїх предметів
        print(f"Середній бал, який ставить викладач з ID {teacher_id} зі своїх предметів: {select_8(teacher_id):.2f}")  # Видалено session
        print()

        # 9. Знайти список курсів, які відвідує певний студент
        print(f"Список курсів, які відвідує студент з ID {student_id}:")
        for subject in select_9(student_id):  
            print(f"- {subject.name}")
        print()

        # 10. Список курсів, які певному студенту читає певний викладач
        print(f"Список курсів, які студенту з ID {student_id} читає викладач з ID {teacher_id}:")
        for subject in select_10(student_id, teacher_id):  
            print(f"- {subject.name}")
            

    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_session()

if __name__ == "__main__":
    test_queries()
