from flask import request, jsonify, Blueprint
from .models import db, Staff,  Student, Payment, Fee, BusPayment, BusDestination, Term, Gallery, Event, Notification, student_bus_destination
from flask import current_app as app
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError


logging.basicConfig(level=logging.DEBUG)
routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        identifier = data.get('identifier')  # admission_number or name
        password = data.get('password')

        if not identifier or not password:
            return jsonify({"error": "Missing identifier or password"}), 400

        # Check if it's a student login
        student = Student.query.filter_by(admission_number=identifier).first()
        if student and student.check_password(password):
            return jsonify({"message": "Student login successful", "role": "student"}), 200

        # Check for staff login
        staff = Staff.query.filter_by(name=identifier).first()
        if staff and staff.check_password(password):
            return jsonify({"message": "Staff login successful", "role": staff.role}), 200

        # If no match is found
        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        app.logger.error(f"Error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500
    # return jsonify({"message": "Invalid credentials"}), 401
# Add/Register Student
@routes.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    required_fields = ['name', 'admission_number', 'grade_id', 'phone', 'term_fee', 'use_bus', 'is_boarding']

    # Input validation
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400

    # Check if grade exists
    grade = Grade.query.get(data['grade_id'])
    if not grade:
        return jsonify({"error": "Invalid grade ID"}), 400

    try:
        # Create new student
        student = Student(
            name=data['name'],
            admission_number=data['admission_number'],
            grade_id=data['grade_id'],
            phone=data['phone'],
            term_fee=data['term_fee'],
            use_bus=data['use_bus'],
            is_boarding=data['is_boarding'],
            arrears=data.get('arrears', 0.0),
            bus_balance=data.get('bus_balance', 0.0),
            created_at=datetime.utcnow()
        )
        # Set password to admission number
        student.set_password(data['admission_number'])

        # Initialize balance
        student.initialize_balance()

        # Commit to database
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student added successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Admission number must be unique"}), 400
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@routes.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.name for student in students])

@routes.route('/students/<int:id>', methods=['GET'])
# Update Student
@routes.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    # Update fields
    if 'name' in data:
        student.name = data['name']
    if 'phone' in data:
        student.phone = data['phone']
    if 'use_bus' in data:
        student.use_bus = data['use_bus']
    if 'is_boarding' in data:
        student.is_boarding = data['is_boarding']

    # Reinitialize balance if necessary
    if 'is_boarding' in data or 'arrears' in data:
        student.arrears = data.get('arrears', student.arrears)
        student.initialize_balance()

    # Commit changes
    db.session.commit()
    return jsonify({"message": "Student updated successfully"}), 200


# Delete Student
@routes.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 200


# Update Balance After Payment
@routes.route('/students/<int:student_id>/update-balance', methods=['POST'])
def update_balance(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    payment_amount = data.get('payment_amount')
    if not payment_amount or payment_amount <= 0:
        return jsonify({"error": "Valid payment amount is required"}), 400

    # Record the payment
    payment = Payment(student_id=student.id, amount=payment_amount, date=datetime.utcnow())
    db.session.add(payment)

    # Update student balance
    student.balance -= payment_amount
    if student.balance < 0:
        student.balance = 0

    db.session.commit()
    return jsonify({"message": "Student balance updated successfully"}), 200
    
@routes.route('/register_staff', methods=['POST'])
def register_staff():
    data = request.get_json()
    name = data['name']
    phone = data['phone']
    role = data['role']
    password = data.get('password', 'defaultpassword')  # Set default password if not provided
    
    staff = Staff(
        name=name,
        phone=phone,
        role=role,
    )
    staff.set_password(password)  # Set password using bcrypt
    db.session.add(staff)
    db.session.commit()
    
    return jsonify({"message": "Staff registered successfully"}), 201

def get_staff():
    staff_members = Staff.query.all()
    return jsonify([{
        'id': staff.id,
        'name': staff.name,
        'phone': staff.phone,
        'role': staff.role,
        'password':staff.password
    } for staff in staff_members])

@routes.route('/delete_staff/<int:id>', methods=['DELETE'])
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    
    return jsonify({"message": "Staff deleted successfully"}), 200

@routes.route('/fees', methods=['POST'])
def create_fee():
    data = request.get_json()
    term_id = data['term_id']
    grade = data['grade']
    amount = data['amount']

    fee = Fee(term_id=term_id, grade=grade, amount=amount)
    db.session.add(fee)
    db.session.commit()

    return jsonify({
        'message': 'Fee record created successfully',
        'fee': {
            'term_id': term_id,
            'grade': grade,
            'amount': amount
        }
    })

@routes.route('/fees/<int:term_id>', methods=['GET'])
def get_fees_for_term(term_id):
    fees = Fee.query.filter_by(term_id=term_id).all()
    return jsonify([{
        'id': fee.id,
        'grade': fee.grade,
        'amount': fee.amount,
        'is_paid': fee.is_paid
    } for fee in fees])
    
def get_student(id):
    student = Student.query.get(id)
    if student:
        return jsonify({
            'id': student.id,
            'name': student.name,
            'grade': student.grade,
            'balance': student.balance,
            'bus_balance': student.bus_balance,
            'is_boarding': student.is_boarding
        })
    return jsonify({"error": "Student not found"}), 404


# Add Payment
@routes.route('/payments', methods=['POST'])
def add_payment():
    data = request.get_json()
    try:
        student_id = data.get('student_id')
        amount = data.get('amount')
        method = data.get('method')
        term_id = data.get('term_id')
        description = data.get('description')
        notes = data.get('notes')

        if not all([student_id, amount, method, term_id]):
            return jsonify({"error": "Missing required fields"}), 400

        payment = Payment.record_payment(
            student_id=student_id,
            amount=amount,
            method=method,
            term_id=term_id,
            description=description,
            notes=notes
        )
        return jsonify({"message": "Payment added successfully", "payment_id": payment.id}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while adding payment", "details": str(e)}), 500


# Edit Payment
@routes.route('/payments/<int:payment_id>', methods=['PUT'])
def edit_payment(payment_id):
    data = request.get_json()
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        payment.amount = data.get('amount', payment.amount)
        payment.method = data.get('method', payment.method)
        payment.term_id = data.get('term_id', payment.term_id)
        payment.description = data.get('description', payment.description)
        payment.notes = data.get('notes', payment.notes)

        db.session.commit()
        return jsonify({"message": "Payment updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while updating payment", "details": str(e)}), 500


# Delete Payment
@routes.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        db.session.delete(payment)
        db.session.commit()
        return jsonify({"message": "Payment deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while deleting payment", "details": str(e)}), 500


# Get All Payments for a Student
@routes.route('/payments/student/<int:student_id>', methods=['GET'])
def get_payments_by_student(student_id):
    try:
        payments = Payment.query.filter_by(student_id=student_id).all()
        return jsonify([{
            "id": p.id,
            "amount": p.amount,
            "date": p.date,
            "method": p.method,
            "term_id": p.term_id,
            "balance_after_payment": p.balance_after_payment,
            "description": p.description,
            "notes": p.notes
        } for p in payments]), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching payments", "details": str(e)}), 500


# Get Payment by ID
@routes.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({"error": "Payment not found"}), 404

        return jsonify({
            "id": payment.id,
            "amount": payment.amount,
            "date": payment.date,
            "method": payment.method,
            "term_id": payment.term_id,
            "balance_after_payment": payment.balance_after_payment,
            "description": payment.description,
            "notes": payment.notes
        }), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching payment", "details": str(e)}), 500

@routes.route('/students/<int:student_id>/payments/term/<int:term_id>', methods=['GET'])
def get_student_payments_by_term(student_id, term_id):
    payments = Payment.query.filter_by(student_id=student_id).join(Fee).filter(Fee.term_id == term_id).all()
    return jsonify([
        {
            'id': payment.id,
            'amount': payment.amount,
            'date': payment.date,
            'method': payment.method
        }
        for payment in payments
    ])

@routes.route('/get_student_bus_destinations/<int:student_id>', methods=['GET'])
def get_student_bus_destinations(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    bus_destinations = student.bus_destinations  # Use the relationship to get bus destinations
    result = [{
        'bus_destination': destination.name,
        'charge': destination.charge
    } for destination in bus_destinations]
    
    return jsonify(result), 200

@routes.route('/create-term', methods=['POST'])
def create_term():
    data = request.get_json()
    name = data['name']
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

    term = Term(name=name, start_date=start_date, end_date=end_date)
    db.session.add(term)
    db.session.commit()
    
    return jsonify({"message": "Term created successfully", "term": {
        'id': term.id,
        'name': term.name,
        'start_date': term.start_date,
        'end_date': term.end_date
    }})

@routes.route('/terms', methods=['GET'])
def get_terms():
    terms = Term.query.all()
    return jsonify([{
        'id': term.id,
        'name': term.name,
        'start_date': term.start_date,
        'end_date': term.end_date
    } for term in terms])

@routes.route('/bus-payments', methods=['POST'])
def create_bus_payment():
    data = request.get_json()
    student_id = data['student_id']
    amount = data['amount']
    term_id = data['term_id']
    destination_id = data.get('destination_id', None)

    bus_payment = BusPayment(
        student_id=student_id,
        term_id=term_id,
        amount=amount,
        destination_id=destination_id
    )
    db.session.add(bus_payment)
    db.session.commit()

    # Update the student's bus balance
    bus_payment.update_student_bus_balance()

    return jsonify({
        'message': 'Bus payment created successfully',
        'bus_payment': {
            'student_id': student_id,
            'amount': amount,
            'payment_date': bus_payment.payment_date
        }
    })

@routes.route('/bus-destinations', methods=['GET'])
def get_bus_destinations():
    destinations = BusDestination.query.all()
    return jsonify([{
        'id': destination.id,
        'name': destination.name,
        'charge': destination.charge
    } for destination in destinations])

@routes.route('/assign-student-to-bus', methods=['POST'])
def assign_student_to_bus():
    data = request.get_json()
    student_id = data['student_id']
    destination_id = data['destination_id']

    student = Student.query.get(student_id)
    destination = BusDestination.query.get(destination_id)

    if not student or not destination:
        return jsonify({"error": "Student or Bus Destination not found"}), 404

    # Check if the student is already assigned to this destination
    if destination in student.bus_destinations:
        return jsonify({"message": "Student is already assigned to this bus destination"})

    # Assign the student to the bus destination
    student.bus_destinations.append(destination)
    db.session.commit()

    return jsonify({
        'message': 'Student assigned to bus destination successfully',
        'student_id': student.id,
        'destination_id': destination.id
    })
    
def get_terms():
    terms = Term.query.all()
    return jsonify([{
        'id': term.id,
        'name': term.name,
        'start_date': term.start_date,
        'end_date': term.end_date
    } for term in terms])

def add_gallery_item():
    data = request.get_json()
    image_url = data['image_url']
    description = data.get('description', None)

    gallery_item = Gallery(image_url=image_url, description=description)
    db.session.add(gallery_item)
    db.session.commit()

    return jsonify({
        'message': 'Gallery item added successfully',
        'gallery_item': {
            'image_url': image_url,
            'description': description
        }
    })

@routes.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date,
        'destination': event.destination
    } for event in events])

@routes.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    title = data['title']
    description = data['description']
    date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')  # Convert string to datetime
    destination = data['destination']

    event = Event(title=title, description=description, date=date, destination=destination)
    db.session.add(event)
    db.session.commit()

    return jsonify({
        'message': 'Event created successfully',
        'event': {
            'title': title,
            'description': description,
            'date': event.date,
            'destination': destination
        }
    })

@routes.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = Notification.query.all()
    return jsonify([{
        'id': notification.id,
        'message': notification.message,
        'date': notification.date
    } for notification in notifications])

@routes.route('/notifications', methods=['POST'])
def add_notification():
    data = request.get_json()
    message = data['message']

    notification = Notification(message=message)
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Notification added successfully',
        'notification': {
            'message': message,
            'date': notification.date
        }
    })


