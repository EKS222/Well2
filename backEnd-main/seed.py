from datetime import datetime
from app import create_app, db
from app.models import Student, Grade, Staff, Fee, Class, Term, BusDestination, BoardingFee
import random

def seed_data():
    # Seed term
    term = Term(
        name="Term 1 2025", start_date=datetime(2025, 1, 3), end_date=datetime(2025, 2, 4)
    )
    db.session.add(term)
    db.session.commit()
    print(f"Seeded term: {term.name}")

    # Seed grades
    grades = {}
    grade_names = ["baby", "pp1", "pp2", "1", "2", "3", "4"]
    for name in grade_names:
        grade = Grade(name=name)
        db.session.add(grade)
        grades[name] = grade
    db.session.commit()
    print("Seeded grades:", ", ".join(grade_names))

    # Seed fees for each grade
    term_fees = {
        "baby": 6500,
        "pp1": 7500,
        "pp2": 6500,
        "1": 7000,
        "2": 5000,
        "3": 6500,
        "4": 6500
    }
    for grade_name, amount in term_fees.items():
        fee = Fee(term_id=term.id, grade_id=grades[grade_name].id, amount=amount)
        db.session.add(fee)
    db.session.commit()
    print("Seeded fees for all grades.")

    # Seed bus destinations
    bus_destinations = [
        {"name": "Marangetit", "charge": 1200},
        {"name": "Olesoi", "charge": 1288},
        {"name": "Sigor", "charge": 1000},
    ]
    for destination in bus_destinations:
        db.session.add(BusDestination(name=destination["name"], charge=destination["charge"]))
    db.session.commit()
    print("Seeded bus destinations.")

    # Seed boarding fee
    boarding_fee = BoardingFee(extra_fee=4500)
    db.session.add(boarding_fee)
    db.session.commit()
    print("Seeded boarding fee.")

    # Seed teachers
    teacher_names = ["Teacher A", "Teacher B", "Teacher C", "Teacher D", "Teacher E", "Teacher F"]
    teachers = []
    for name in teacher_names:
        teacher = Staff(name=name, phone=f"0720{name[-1]}000", role="teacher")
        teacher.set_password("teacherpassword")
        db.session.add(teacher)
        teachers.append(teacher)
    db.session.commit()
    print("Seeded teachers.")

    # Seed admin staff
    admin_staff = [
        {"name": "Admin A", "phone": "0720000010", "role": "admin"},
        {"name": "Admin B", "phone": "0720000020", "role": "admin"}
    ]
    for admin in admin_staff:
        staff = Staff(name=admin["name"], phone=admin["phone"], role=admin["role"])
        staff.set_password("adminpassword")
        db.session.add(staff)
    db.session.commit()
    print("Seeded admin staff.")

    # Seed classes and streams
    streams = ["blue", "green"]
    for grade_name, grade in grades.items():
        for stream in streams:
            class_name = f"{grade_name.capitalize()} - {stream.capitalize()}"
            teacher = random.choice(teachers)
            class_ = Class(name=class_name, grade_id=grade.id, staff_id=teacher.id)
            db.session.add(class_)
    db.session.commit()
    print("Seeded classes with streams.")

    # Seed students
    for grade_name, grade in grades.items():
        for stream in streams:
            for i in range(1, 6):  # 5 students per class
                student_name = f"{grade_name.capitalize()} {stream.capitalize()} Student {i}"
                student = Student(
                    name=student_name,
                    admission_number=f"ADM{grade.id}{stream[0]}{i:02d}",
                    grade_id=grade.id,
                    phone=f"07200000{i}",
                    term_fee=term_fees[grade_name],
                    use_bus=random.choice([True, False]),
                    arrears=random.uniform(0, 1000),
                    bus_balance=random.uniform(0, 500)
                )
                student.set_password(f"ADM{grade.id}{stream[0]}{i:02d}")
                student.initialize_balance()
                db.session.add(student)
    db.session.commit()
    print("Seeded students.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()  # Drop all tables (only for testing; remove in production)
        db.create_all()  # Create all tables
        seed_data()

        
        
