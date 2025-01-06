from datetime import datetime
from app import create_app, db
from app.models import Staff

def seed_admin():
    admin = Staff(
        name="Admin User",
        phone="1234567890",
        role="admin"
    )
    # Use the updated set_password method from your model
    admin.set_password("adminpassword")
    db.session.add(admin)
    db.session.commit()
    print("Admin staff seeded successfully!")

if __name__ == "__main__":
    # Create the Flask app and push the context
    app = create_app()
    with app.app_context():
        db.drop_all()  # Drop all tables (for testing only; remove in production)
        db.create_all()  # Recreate tables
        seed_admin()