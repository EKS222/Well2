from datetime import date
from app import db
from app.models import Student, Fee, Term

# Grade Promotion Mapping
GRADE_PROMOTION = {
    "baby class": "pp1",
    "pp1": "pp2",
    "pp2": "1",
}

def process_term_rollover():
    current_date = date.today()
    current_term = Term.query.filter(Term.end_date < current_date).first()

    if current_term:
        new_term = Term.query.filter(Term.start_date > current_date).first()
        if not new_term:
            print("No new term found! Please create the next term.")
            return

        students = Student.query.all()
        for student in students:
            student.arrears += student.balance - student.prepayment
            student.prepayment = 0  # Reset prepayment

            new_fee = Fee.query.filter_by(grade_id=student.grade_id, term_id=new_term.id).first()
            if new_fee:
                student.balance = student.arrears + new_fee.amount
            
            student.bus_arrears += student.bus_balance
        
        db.session.commit()
        print("Term rollover completed.")

def promote_students():
    current_date = date.today()
    if current_date.month == 12 and current_date.day == 31:
        students = Student.query.all()
        for student in students:
            current_grade = student.grade.lower()
            if current_grade in GRADE_PROMOTION:
                student.grade = GRADE_PROMOTION[current_grade]
            else:
                try:
                    numeric_grade = int(current_grade)
                    student.grade = str(numeric_grade + 1)
                except ValueError:
                    print(f"Unable to promote grade: {current_grade}")
        
        db.session.commit()
        print("Student promotions completed.")
              
