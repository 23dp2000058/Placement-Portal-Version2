from extensions import db
from models import User, Role, Student, Company, Jobposition, Application, Placementdrive
from sqlalchemy import or_
class AdminService:
    @staticmethod
    def get_dashboard_stats():
        """Fetch totals for the Admin Dashboard counters"""
        return {
            "total_students": Student.query.count(),
            "total_companies": Company.query.count(),
            "total_job_postings": Jobposition.query.count(),
            "total_applications": Application.query.count()
        }

    @staticmethod
    def search_companies(name=None):
        query = Company.query
        if name:
            query = query.filter(or_(
                Company.name.ilike(f'%{name}%'),
                Company.description.ilike(f'%{name}%')
            ))
        return query.all()
        
    @staticmethod
    def search_students(search_term=None):
        query = Student.query
        if search_term:
            query = query.filter(or_(
                Student.name.ilike(f'%{search_term}%'),
                Student.studentid.ilike(f'%{search_term}%'),
                Student.branch.ilike(f'%{search_term}%')
            ))
        return query.all()



    @staticmethod
    def get_all_applications():
        """NEW: Fetch all applications with student names and statuses for Admin monitoring"""
        apps = Application.query.all()
        return [{
            "application_id": a.applicationid,
            "student_name": a.student.name, # Using the relationship
            "company_name": a.job.company.name,
            "job_title": a.job.title,
            "status": a.application_status,
            "interview_date": a.interview_date.strftime("%Y-%m-%d %H:%M") if a.interview_date else "Not Scheduled",
            "feedback": a.feedback or "No feedback provided"
        } for a in apps]

    @staticmethod
    def approve_company(company_id_str):
        company = Company.query.filter_by(companyid=company_id_str).first()
        if company:
            company.is_approved = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def toggle_user_status(user_id):
        user = User.query.get(user_id)
        if not user:
            return None
        user.active = not user.active
        db.session.commit()
        return user

    @staticmethod
    def get_all_companies():
        """Fetch all companies with their details"""
        companies = Company.query.all()
        return [{
            "id": c.companyid,
            "name": c.name,
            "industry": c.industry,
            "location": c.location,
            "email": c.user.email,
            "is_approved": c.is_approved,
            "is_blacklisted": getattr(c, 'is_blacklisted', False),
            "HR_contact": c.HR_contact
        } for c in companies]

    @staticmethod
    def get_all_students():
        """Fetch all students with their details"""
        students = Student.query.all()
        return [{
            "id": s.studentid,
            "name": s.name,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "year": s.year,
            "email": s.user.email,
            "is_blacklisted": s.is_blacklisted
        } for s in students]

    @staticmethod
    def get_pending_company_applications():
        """Fetch pending company registrations"""
        companies = Company.query.filter_by(is_approved=False).all()
        return [{
            "id": c.companyid,
            "company_name": c.name,
            "industry": c.industry,
            "email": c.user.email,
            "HR_contact": c.HR_contact
        } for c in companies]

    @staticmethod
    def delete_company(company_id):
        """Delete a company and its related data"""
        company = Company.query.filter_by(companyid=company_id).first()
        if not company:
            return False
        try:
            # Delete associated applications
            Application.query.filter_by(company_id=company_id).delete()
            # Delete associated jobs
            Jobposition.query.filter_by(companyid=company_id).delete()
            # Delete associated drives
            Placementdrive.query.filter_by(companyid=company_id).delete()
            # Delete user account
            User.query.filter_by(id=company.user_id).delete()
            # Delete company
            db.session.delete(company)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def delete_student(student_id):
        """Delete a student and their related data"""
        student = Student.query.filter_by(studentid=student_id).first()
        if not student:
            return False
        try:
            # Delete associated applications
            Application.query.filter_by(studentid=student_id).delete()
            # Delete user account
            User.query.filter_by(id=student.user_id).delete()
            # Delete student
            db.session.delete(student)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def blacklist_update_status(entity_type, entity_id, status: bool):
        """
        Blacklist/activate a student or company.
        If a company is blacklisted, cancel all of its approved/active drives.
        """
        # 1) Resolve target by type (uses actual column names)
        if entity_type == 'student':
            target = Student.query.filter_by(studentid=entity_id).first()
        elif entity_type == 'company':
            target = Company.query.filter_by(companyid=entity_id).first()
        else:
            return False, "Invalid type"

        if not target:
            return False, "Not found"

        # 2) Update blacklist flag (Student has is_blacklisted; Company can be treated similarly)
        # For Students you already have is_blacklisted in the model.
        # For Companies, if you don't have is_blacklisted, you can optionally add one; otherwise we just proceed to cancel drives on 'status=True'.
        if hasattr(target, 'is_blacklisted'):
            target.is_blacklisted = status

        # 3) On company blacklist, cancel its approved drives by changing driveapprovalstatus
        if entity_type == 'company' and status is True:
            # Company.companyid -> Placementdrive.companyid
            (
                Placementdrive.query
                .filter_by(companyid=entity_id, driveapprovalstatus='approved')
                .update({'driveapprovalstatus': 'cancelled'}, synchronize_session=False)
            )

        db.session.commit()
        return True, f"{entity_type.capitalize()} blacklist status set to {status}"
