from flask_restful import Resource
from flask_security import auth_required, roles_accepted, current_user
from flask import jsonify, request
from models import Application

class ApplicationDetailAPI(Resource):
    @auth_required('token')
    def get(self, application_id):
        """Get details of a specific application"""
        app = Application.query.filter_by(applicationid=application_id).first()
        if not app:
            return {"message": "Application not found"}, 404
        
        return jsonify({
            "id": app.applicationid,
            "student_name": app.student.name if app.student else "Unknown",
            "student_email": app.student.user.email if app.student and app.student.user else "Unknown",
            "department": app.student.branch if app.student else "Unknown",
            "company_name": app.job.company.name if app.job and app.job.company else "Unknown",
            "position": app.job.title if app.job else "Unknown",
            "drive_name": app.job.title if app.job else "Unknown",
            "applied_date": app.applied_at.strftime("%Y-%m-%d") if app.applied_at else None,
            "status": app.application_status,
            "result": app.feedback,
            "offer_letter": app.offer_letter_path,
            "cgpa": app.student.cgpa if app.student else 0,
            "backlog": "None",
            "skills": app.student.skills if app.student else "Not specified",
            "resume": app.student.resume_link if app.student else None
        }), 200

    @auth_required('token')
    def put(self, application_id):
        """Update application status"""
        app = Application.query.filter_by(applicationid=application_id).first()
        if not app:
            return {"message": "Application not found"}, 404
        
        data = request.get_json()
        
        # Check if user is authorized (company or admin)
        if hasattr(current_user, 'roles'):
            allowed_roles = [role.name for role in current_user.roles]
            if 'company' not in allowed_roles and 'admin' not in allowed_roles:
                return {"message": "Access denied"}, 403
        
        # Update status if provided
        if 'status' in data:
            app.application_status = data['status']
        
        # Update other fields if provided
        if 'feedback' in data:
            app.feedback = data['feedback']
        if 'interview_date' in data:
            app.interview_date = data['interview_date']
        if 'offer_letter' in data:
            app.offer_letter_path = data['offer_letter']
        
        try:
            from extensions import db
            db.session.commit()
            return {"message": "Application updated successfully"}, 200
        except Exception as e:
            from extensions import db
            db.session.rollback()
            return {"message": str(e)}, 400
