from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    bus_payments = db.relationship('BusPayment', back_populates='term', lazy=True)
    
    def __repr__(self):
        return f"<Term(name={self.name}, start_date={self.start_date}, end_date={self.end_date})>"

student_bus_destination = db.Table(
    'student_bus_destination',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('bus_destination_id', db.Integer, db.ForeignKey('bus_destination.id'), primary_key=True)  # Correct table name
)

# Staff can represent many classes
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Password field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), nullable=False)
    # Represent many classes (one-to-many relationship)
    classes = db.relationship('Class', back_populates='staff')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
# Each student can have many payments, bus payments, and assignments
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    arrears = db.Column(db.Float, default=0.0)
    term_fee = db.Column(db.Float, nullable=False)
    use_bus = db.Column(db.Boolean, nullable=False)
    bus_balance = db.Column(db.Float, default=0.0)
    password = db.Column(db.String(100), nullable=False)
    
         # Relationships
    bus_destinations = db.relationship('BusDestination', secondary=student_bus_destination, back_populates='students')
    payments = db.relationship('Payment', backref='student', lazy=True)
    bus_payments = db.relationship('BusPayment', back_populates='student', lazy=True)
    assignments = db.relationship('Assignment', backref='student', lazy=True)

    def set_password(self, password):
        """Set password using bcrypt."""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if the password matches."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def initialize_balance(self):
        fee = Fee.query.filter_by(grade=self.grade).first()
        if fee:
            self.balance = (fee.term_fee or 0) + (self.arrears or 0)
        else:
            self.balance = self.arrears  # or set it to 0.0, or whatever is appropriate# Fee model where each grade can have only one fee (One-to-One for grade)

# Payment model where students can have many payments
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)  # Foreign key to Student
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    method = db.Column(db.String(15))

    @staticmethod
    def record_payment(student_id, amount, method):
        student = Student.query.get(student_id)
        if not student:
            raise ValueError("Student not found")
        student.balance -= amount
        student.arrears = 0  # Reset arrears on payment
        payment = Payment(student_id=student_id, amount=amount, method=method)
        db.session.add(payment)
        db.session.commit()
        return payment

# Boarding fees, linked to grades
class BoardingFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(10), nullable=False)
    extra_fee = db.Column(db.Float, nullable=False, default=3500)

    def __repr__(self):
        return f'<BoardingFee {self.grade} - {self.extra_fee}>'


# Assignments can be related to multiple students
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)  # Foreign key to Student

    def __repr__(self):
        return f'<Assignment {self.title} for Grade {self.grade}>'


# Class model to represent the classes that staff can manage
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)  # One-to-Many relationship to Staff
    staff = db.relationship('Staff', back_populates='classes')


    def __repr__(self):
        return f'<Class {self.name}>'


# School Events
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'

# Notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} - {self.message}>'
    


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Fee(term_id={self.term_id}, grade={self.grade}, amount={self.amount}, is_paid={self.is_paid})>"


class BusDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    charge = db.Column(db.Float, nullable=False)  # The bus charge for this destination
    
    # Many-to-many relationship with students
    students = db.relationship('Student', secondary=student_bus_destination, back_populates='bus_destinations')

    def __repr__(self):
        return f"<BusDestination(name={self.name}, charge={self.charge})>"

class BusPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('bus_destination.id'), nullable=True)  # Correct table name
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
    
class Gallery(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<Gallery(image_url={self.image_url}, description={self.description})>"