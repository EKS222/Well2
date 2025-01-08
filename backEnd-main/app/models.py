from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

# Term model
class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    bus_payments = db.relationship('BusPayment', back_populates='term', lazy=True)

    def __repr__(self):
        return f"<Term(name={self.name}, start_date={self.start_date}, end_date={self.end_date})>"

# Association table for students and bus destinations
student_bus_destination = db.Table(
    'student_bus_destination',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('bus_destination_id', db.Integer, db.ForeignKey('bus_destination.id'), primary_key=True)
)

# Staff model
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), nullable=False)

    classes = db.relationship('Class', back_populates='staff')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Grade model for fee structure
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)
    term_fees = db.relationship('Fee', back_populates='grade', lazy=True)

    def __repr__(self):
        return f"<Grade(name={self.name})>"

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False
    balance = db.Column(db.Float, default=0.0)
    arrears = db.Column(db.Float, default=0.0)
    term_fee = db.Column(db.Float, nullable=False)
    use_bus = db.Column(db.Boolean, nullable=False)
    bus_balance = db.Column(db.Float, default=0.0)
    is_boarding = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(100), nullable=False)

    # Relationships
    grade = db.relationship('Grade', backref='students')
    bus_destinations = db.relationship('BusDestination', secondary=student_bus_destination, back_populates='students')
    payments = db.relationship('Payment', backref='student', lazy=True)
    bus_payments = db.relationship('BusPayment', back_populates='student', lazy=True)
    assignments = db.relationship('Assignment', backref='student', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def initialize_balance(self):
        """
        Calculate the student's term balance based on their grade, boarding status, and arrears.
        """
        # Fetch the term fee for the student's grade
        fee = Fee.query.filter_by(grade_id=self.grade_id).first()
        if not fee:
            raise ValueError("Fee structure not set for this grade.")

        # Default balance
        self.balance = fee.amount
        # Students below grade 5 who choose to board pay an additional fee
        if self.is_boarding and int(self.grade.name) < 5:
            boarding_fee = BoardingFee.query.first()
            if boarding_fee:
                self.balance += boarding_fee.extra_fee

        # Add any arrears to the balance
        if self.arrears:
            self.balance += self.arrears

        db.session.commit()

    def update_bus_balance(self, payment_amount):
        """
        Update the student's bus balance after a payment.
        """
        if not self.use_bus:
            raise ValueError("Student does not use the bus.")
        
        self.bus_balance -= payment_amount
        if self.bus_balance < 0:
            self.bus_balance = 0

        db.session.commit()
        
        
# Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    method = db.Column(db.String(15), nullable=False)
    term_id = db.Column(db.String(20), nullable=False)
    balance_after_payment = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    notes = db.Column(db.Text)

    @staticmethod
    def record_payment(student_id, amount, method, term_id, description=None, notes=None):
        from models import Student

        student = Student.query.get(student_id)
        if not student:
            raise ValueError("Student not found")

        student.balance -= amount
        if student.balance <= 0:
            student.arrears = 0  # Clear arrears if fully paid

        payment = Payment(
            student_id=student_id,
            amount=amount,
            method=method,
            term_id=term_id,
            balance_after_payment=student.balance,
            description=description,
            notes=notes
        )
        db.session.add(payment)
        db.session.commit()

        return payment

# Fee model for each term and grade
class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)

    grade = db.relationship('Grade', back_populates='term_fees')

    def __repr__(self):
        return f"<Fee(term_id={self.term_id}, grade_id={self.grade_id}, amount={self.amount}, is_paid={self.is_paid})>"

# Boarding Fee model linked to grade
class BoardingFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    extra_fee = db.Column(db.Float, nullable=False, default=3500)

    def __repr__(self):
        return f'<BoardingFee {self.grade_id} - {self.extra_fee}>'

# Assignment model related to multiple students
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    grade_id = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f'<Assignment {self.title} for Grade {self.grade_id}>'

# Class model related to staff
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    staff = db.relationship('Staff', back_populates='classes')
    grade = db.relationship('Grade', backref='classes')

    def __repr__(self):
        return f'<Class {self.name}>'

# Gallery model for images
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Gallery(image_url={self.image_url}, description={self.description})>"

# Bus Destination model
class BusDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    charge = db.Column(db.Float, nullable=False)

    students = db.relationship('Student', secondary=student_bus_destination, back_populates='bus_destinations')

    def __repr__(self):
        return f"<BusDestination(name={self.name}, charge={self.charge})>"

# Bus Payment model
class BusPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('bus_destination.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='bus_payments')
    term = db.relationship('Term', back_populates='bus_payments')
    destination = db.relationship('BusDestination', backref='payments')

    def __init__(self, student_id, term_id, amount, destination_id=None):
        self.student_id = student_id
        self.term_id = term_id
        self.amount = amount
        self.destination_id = destination_id
        student = Student.query.get(student_id)
        if student:
            student.bus_balance -= amount
            db.session.commit()

    def __repr__(self):
        return f"<BusPayment(student_id={self.student_id}, term_id={self.term_id}, destination_id={self.destination_id}, amount={self.amount}, payment_date={self.payment_date})>"

# Notifications model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} - {self.message}>'
