import os
from dotenv import load_dotenv
import uuid
from app import create_app
from extensions import db
from models import User, Role, Company, Student, Placementdrive, Jobposition
from flask_security import hash_password

# load environment variables from .env if present
load_dotenv()

def seed_data():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 1. Ensure Roles exist
        roles = {}
        for r_name in ['admin', 'student', 'company']:
            role = Role.query.filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name, description=f"{r_name.capitalize()} Role")
                db.session.add(role)
            roles[r_name] = role
        db.session.commit()

        # 2. Helper to create Users
        def create_user(email, password, role_name):
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    password=hash_password(password),
                    fs_uniquifier=str(uuid.uuid4()),
                    active=True
                )
                user.roles.append(roles[role_name])
                db.session.add(user)
                db.session.flush()
            return user

        # 3. Create admin user from environment (if specified)
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@study')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        create_user(admin_email, admin_password, 'admin')

        # 4. Create 3 Companies with different statuses
        # Company A: Approved with Drive
        u1 = create_user('hr@techcorp.com', 'pass123', 'company')
        c1 = Company(user_id=u1.id, name="TechCorp", industry="IT", location="Bangalore", 
                     HR_contact="Rajesh", companyid="COMP_TC", is_approved=True)
        db.session.add(c1)

        # Company B: Pending Approval
        u2 = create_user('hr@startup.io', 'pass123', 'company')
        c2 = Company(user_id=u2.id, name="Greenfield Startup", industry="Fintech", location="Mumbai", 
                     HR_contact="Sita", companyid="COMP_GS", is_approved=False)
        db.session.add(c2)

        # Company C: Approved without Drive
        u3 = create_user('hr@bluechip.com', 'pass123', 'company')
        c3 = Company(user_id=u3.id, name="BlueChip Solutions", industry="Consulting", location="Delhi", 
                     HR_contact="Amit", companyid="COMP_BC", is_approved=True)
        db.session.add(c3)

        # 4. Create 10 Students
        student_names = [
            "Aarav Sharma", "Ishani Gupta", "Vihaan Reddy", "Ananya Verma", 
            "Kabir Singh", "Mira Nair", "Arjun Das", "Sana Khan", 
            "Rohan Mehta", "Zoya Ahmed"
        ]
        
        for i, name in enumerate(student_names):
            email = f"student{i+1}@iit.ac.in"
            stu_user = create_user(email, 'student123', 'student')
            profile = Student(
                studentid=f"2026_STU_{i+1:03}",
                user_id=stu_user.id,
                name=name,
                branch="Computer Science" if i % 2 == 0 else "Data Science",
                cgpa=8.0 + (i * 0.1),
                year=2026
            )
            db.session.add(profile)

        # 5. Create a Drive for TechCorp
        db.session.flush()
        drive = Placementdrive(
            driveid="DRIVE_2026_TC",
            companyid=c1.companyid,
            drivedate=db.func.current_timestamp(),
            driveapprovalstatus='approved'
        )
        db.session.add(drive)

        db.session.commit()
        print("🚀 Seeded: 3 Companies, 10 Students, and 1 Active Drive.")

if __name__ == "__main__":
    seed_data()