from sqlalchemy import func, desc
from typing import List, Tuple
from models import Student, Grade, Group, Subject  
from connect import session, close_session
from typing import Union, Tuple

# Загальна функція для знаходження студентів із середнім балом
def get_students_avg_grade(filter_conditions: list = [], limit: int = None) -> List[Tuple[str, float]]:
    query = session.query(Student.name, func.avg(Grade.grade).label("avg_grade")).join(Grade)
    
    for condition in filter_conditions:
        query = query.filter(condition)
    
    query = query.group_by(Student.id).order_by(desc("avg_grade"))
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

# Знайти 5 студентів із найбільшим середнім балом
def select_1() -> List[Tuple[str, float]]:
    return get_students_avg_grade(limit=5)

# Знайти студента із найвищим середнім балом з певного предмета
def select_2(subject_id: int) -> Union[Tuple[str, float], None]:
    return get_students_avg_grade(
        filter_conditions=[Grade.subject_id == subject_id], limit=1
    )[0] if get_students_avg_grade(
        filter_conditions=[Grade.subject_id == subject_id], limit=1
    ) else None

# Знайти середній бал у групах з певного предмета
def select_3(subject_id: int) -> List[Tuple[str, float]]:
    result = (
        session.query(Group.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Group.students)
        .join(Grade)
        .filter(Grade.subject_id == subject_id)
        .group_by(Group.name)
        .all()
    )
    return result

# Знайти середній бал на потоці
def select_4() -> float:
    return session.query(func.avg(Grade.grade)).scalar()

# Загальна функція для отримання курсів
def get_courses(filter_conditions: list = []) -> List[Subject]:
    return session.query(Subject).filter(*filter_conditions).all()

# Знайти які курси читає певний викладач
def select_5(teacher_id: int) -> List[Subject]:
    return get_courses(filter_conditions=[Subject.teacher_id == teacher_id])

# Знайти список студентів у певній групі
def select_6(group_id: int) -> List[Student]:
    return session.query(Student).filter(Student.group_id == group_id).all()

# Знайти оцінки студентів у окремій групі з певного предмета
def select_7(group_id: int, subject_id: int) -> List[Tuple[Student, Grade]]:
    return (
        session.query(Student, Grade)
        .join(Grade)
        .filter(Student.group_id == group_id, Grade.subject_id == subject_id)
        .all()
    )

# Знайти середній бал, який ставить певний викладач
def select_8(teacher_id: int) -> float:
    return (
        session.query(func.avg(Grade.grade))
        .join(Subject)
        .filter(Subject.teacher_id == teacher_id)
        .scalar()
    )

# Знайти список курсів, які відвідує певний студент
def select_9(student_id: int) -> List[Subject]:
    return get_courses(
        filter_conditions=[Grade.student_id == student_id]
    )

# Список курсів, які певному студенту читає певний викладач
def select_10(student_id: int, teacher_id: int) -> List[Subject]:
    return get_courses(
        filter_conditions=[Grade.student_id == student_id, Subject.teacher_id == teacher_id]
    )

close_session()
