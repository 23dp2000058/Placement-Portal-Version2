from app import app
from models import db, User, Role
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

def initialize_database():
    with app.app_context():
        # 1. Create tables if they don't exist (does NOT delete existing data)
        print("Checking database tables...")
        db.drop_all()  # Drop all tables to ensure a clean slate for testing
        db.create_all()
        
        datastore: SQLAlchemyUserDatastore = app.datastore

        # 2. Define Roles and ensure they exist
        roles_to_create = [
            {'name': 'admin', 'description': 'Superuser with full access'},
            {'name': 'student', 'description': 'Student user for placements'},
            {'name': 'company', 'description': 'Company representative'}
        ]

        print("Syncing roles...")
        for r in roles_to_create:
            if not datastore.find_role(r['name']):
                datastore.create_role(name=r['name'], description=r['description'])
                print(f"Created role: {r['name']}")
            else:
                print(f"Role '{r['name']}' already exists. Skipping.")

        # 3. Create Admin from Environment Variables
        admin_email = app.config.get("ADMIN_EMAIL")
        admin_pass = app.config.get("ADMIN_PASSWORD")

        if admin_email and admin_pass:
            if not datastore.find_user(email=admin_email):
                admin_role = datastore.find_role('admin')
                datastore.create_user(
                    email=admin_email,
                    password=hash_password(admin_pass),
                    roles=[admin_role],
                    active=True
                )
                print(f"Admin user '{admin_email}' created.")
            else:
                print(f"Admin '{admin_email}' already exists. Skipping.")
        else:
            print("Warning: ADMIN_EMAIL or ADMIN_PASSWORD missing from .env")

        # 4. Create Dummy/Default Data (Only if not already there)
        default_users = [
            {"email": "student@study", "password": "studentpassword", "role": "student"},
            {"email": "company@study", "password": "companypassword", "role": "company"}
        ]

        for u in default_users:
            if not datastore.find_user(email=u['email']):
                target_role = datastore.find_role(u['role'])
                datastore.create_user(
                    email=u['email'],
                    password=hash_password(u['password']),
                    roles=[target_role],
                    active=True
                )
                print(f"Created default user: {u['email']}")

        # 5. Final Commit
        try:
            db.session.commit()
            print("Database initialization successful!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")

if __name__ == "__main__":
    initialize_database()