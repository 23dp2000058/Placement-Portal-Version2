from flask import Blueprint, request, jsonify, current_app
from flask_security.utils import hash_password, verify_password
from models import db, User, Role, Student, Company
import uuid
auth_bp = Blueprint("auth",__name__,url_prefix='/auth')   
@auth_bp.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    email =data["email"]
    password = data["password"]

    if (not email or not password ):
        return {"message" : "invalid input"}
    user = User.query.filter_by(email=email).first()
    if not user:
        return {"message": "user not found"}, 404
    if not verify_password(password, user.password):
        return {"message" : "invalid credentials"},400
    
    return {
            "id": user.id,
            "email": user.email,
            "access_token": user.get_auth_token(),
            "role": user.roles[0].name
        },200

@auth_bp.route("/register",methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role")
    if not email or not password or role_name not in ["student", "company"]:
        return {"message": "Invalid input: role must be student or company"}, 400
    if User.query.filter_by(email=email).first():
        return {"message": "User already exists"}, 400
    datastore = current_app.extensions['security'].datastore
    is_active = False if role_name == "company" else True
    try:
        role = datastore.find_role(role_name)
        
        # 1. Create the User (Already in your code)
        user = datastore.create_user(
            email=email,
            password=hash_password(password),
            roles=[role],
            active=is_active
        )
        
        # 2. Flush to get the user.id without ending the transaction
        db.session.flush() 

        # 3. Add the Profile Logic
        if role_name == "student":
            new_student = Student(
                studentid=f"STU_{uuid.uuid4().hex[:6].upper()}", # Generates unique ID
                user_id=user.id, # Links to the user we just created
                name=data.get("name", "New Student"),
                branch=data.get("branch", "N/A"),
                year=data.get("year", 2026),
                cgpa=data.get("cgpa", 0.0)
            )
            db.session.add(new_student)
            
        elif role_name == "company":
            new_company = Company(
                companyid=f"COMP_{uuid.uuid4().hex[:6].upper()}",
                user_id=user.id,# Links to the user we just created
                name=data.get("name"), # Required
                industry=data.get("industry", "N/A"), # Required
                location=data.get("location", "N/A"), # Required
                HR_contact=data.get("HR_contact", email), # Required
                description=data.get("description", ""),
                is_approved=False # Important: Admin must approve later
            )
            db.session.add(new_company)

        # 4. Final Commit for both User and Profile
        db.session.commit()
        
        if not is_active:
            return {"message": "Company registered. Pending Admin approval."}, 201
        return {"message": f"{role_name} registered successfully"}, 201

    except Exception as e:
        db.session.rollback()
        return {"message": "Error creating user", "error": str(e)}, 500
    

