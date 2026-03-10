from datetime import datetime, timezone
import uuid
from extensions import db
from flask_security import UserMixin, RoleMixin

class MyBase(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True) # Real PK for all tables
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))

class User(MyBase, UserMixin):
    __tablename__ = 'user'
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean(), default=True) # For Blacklisting
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

class Role(MyBase, RoleMixin):
    __tablename__ = 'role'
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=False)

class UserRoles(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

class Company(MyBase):
    __tablename__ = 'company'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    weblink = db.Column(db.String(200))
    HR_contact = db.Column(db.String(200), nullable=False)
    companyid = db.Column(db.String(30), nullable=False, unique=True) # String ID for display
    is_approved = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text) 
    logo_url = db.Column(db.String(500))
    drives = db.relationship('Placementdrive', backref='company', lazy='subquery')
    jobs = db.relationship('Jobposition', backref='company', lazy='subquery')
    user = db.relationship('User', backref=db.backref('company', uselist=False))

class Student(db.Model):
    __tablename__ = 'student'
    studentid = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)  # <-- Add this line
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    # ... other columns
    year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(30), nullable=False)
    # ADDED: Milestone Profile Fields
    skills = db.Column(db.String(500))
    resume_link = db.Column(db.String(500))
    education_history = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    applications = db.relationship('Application', backref='student', lazy='subquery')
    is_blacklisted = db.Column(db.Boolean, default=False)

class Placementdrive(MyBase):
    __tablename__ = 'placementdrive'
    # Use id from MyBase as PK; driveid is unique string for business logic
    driveid = db.Column(db.String(30), nullable=False, unique=True) 
    companyid = db.Column(db.String(30), db.ForeignKey('company.companyid'), nullable=False)
    drivedate = db.Column(db.DateTime, nullable=False)
    driveapprovalstatus = db.Column(db.String(20), nullable=False, default='pending')
    jobs_offered = db.relationship('Jobposition', backref='parentdrive', lazy='subquery')
    

class Jobposition(MyBase):
    __tablename__ = 'jobposition'
    # Use id from MyBase as PK; jobid is unique string for business logic
    jobid = db.Column(db.String(30), nullable=False, unique=True)
    companyid = db.Column(db.String(30), db.ForeignKey('company.companyid'), nullable=False)
    salary = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    drive_id = db.Column(db.String(30), db.ForeignKey('placementdrive.driveid'), nullable=False)
    skills_required = db.Column(db.String(300), nullable=False)
    apps = db.relationship('Application', backref='job', lazy='subquery')
    job_description = db.Column(db.Text, nullable=False)
    eligible_branches = db.Column(db.String(500), default="All")
    job_location = db.Column(db.String(200), nullable=False)

class Application(MyBase):
    __tablename__ = 'application'
    # Use id from MyBase as PK; applicationid is unique string for business logic
    applicationid = db.Column(db.String(30), nullable=False, unique=True)
    jobid = db.Column(db.String(30), db.ForeignKey('jobposition.jobid'), nullable=False)
    studentid = db.Column(db.String(30), db.ForeignKey('student.studentid'), nullable=False)
    application_status = db.Column(db.String(20), nullable=False, default='Applied')
    offer_letter_path = db.Column(db.String(500), nullable=True) #
    interview_date = db.Column(db.DateTime, nullable=True) #
    feedback = db.Column(db.Text, nullable=True) #
    applied_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    company_id = db.Column(db.String(30), db.ForeignKey('company.companyid'), nullable=False)
    drive_id = db.Column(db.String(30), db.ForeignKey('placementdrive.driveid'), nullable=False)
    company_rel = db.relationship('Company', foreign_keys=[company_id])
    drive_rel = db.relationship('Placementdrive', foreign_keys=[drive_id])
    __table_args__ = (db.UniqueConstraint('studentid', 'jobid', name='_student_job_uc'),)