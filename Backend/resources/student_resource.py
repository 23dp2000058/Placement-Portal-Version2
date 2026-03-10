# path: resources/student_resource.py
from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted, current_user
from flask import jsonify, request
from services.student_service import StudentService
from models import Student, Application
from extensions import db

class StudentProfile(Resource):
    # Use token auth consistently; allow only students
    method_decorators = [auth_required('token'), roles_accepted('student')]

    def put(self):
        """Update student profile fields (skills, education_history, resume_link)."""
        data = request.get_json() or {}
        # current_user.id -> Student.user_id
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404

        success, msg = StudentService.update_student_profile(
            user_id=current_user.id,
            data=data
        )
        return ({"message": msg}, 200) if success else ({"message": msg}, 400)


class StudentJobAction(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def post(self, job_id):
        """Apply for a specific job posting."""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404

        success, msg = StudentService.apply_for_job(student.studentid, job_id)
        # Created when application is new; bad request if duplicate/not eligible
        return ({"message": msg}, 201) if success else ({"message": msg}, 400)


class StudentDashboard(Resource):
    @auth_required('token')
    @roles_required('student')
    def get(self):
        """Student dashboard: profile summary + applications + job availability."""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404

        jobs_data = StudentService.get_jobs_with_status(student.studentid)
        applications = Application.query.filter_by(studentid=student.studentid).all()

        return {
            "profile": {
                "name": student.name or student.user.email,
                "cgpa": student.cgpa,
                "branch": student.branch
            },
            "jobs_available": jobs_data,
            "my_applications": [{
                "id": a.applicationid,
                "job": a.job.title if a.job else "Unknown",
                "status": a.application_status,
                "offer": a.offer_letter_path is not None
            } for a in applications]
        }


class StudentPlacementHistoryAPI(Resource):
    # Ensure only students can access, with token auth first
    method_decorators = [auth_required('token'), roles_accepted('student')]

    def get(self):
        """Fetch the placement/application history for the logged-in student."""
        # Resolve the student's business identifier
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found", "history": []}, 200

        history = StudentService.get_placement_history(student.studentid)
        if not history:
            return {"message": "No placement history found", "history": []}, 200
        return {"history": history}, 200


class JobBoardAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self):
        """Fetch jobs visible to students (e.g., from approved companies / approved drives)."""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404

        jobs = StudentService.get_jobs_with_status(student.studentid)
        # Return the list directly so the Vue page can render it without extra property access.
        return jobs, 200


class StudentProfileAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self):
        """Get student profile"""
        profile = StudentService.get_student_profile(current_user.id)
        if not profile:
            return {"message": "Student profile not found"}, 404
        return profile


class StudentDrivesAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self):
        """Get available drives for student"""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404
        
        drives = StudentService.get_available_drives(student.studentid)
        return drives


class StudentAppliedDrivesAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self):
        """Get drives student has applied to"""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404
        
        applied = StudentService.get_applied_drives(student.studentid)
        return applied


class StudentApplicationHistoryAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self):
        """Get detailed application history"""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404
        
        history = StudentService.get_application_history(student.studentid)
        return history


class StudentCheckApplicationAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def get(self, job_id):
        """Check if student has already applied to a job"""
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404
        
        has_applied = StudentService.check_if_applied(student.studentid, job_id)
        return {"has_applied": has_applied}, 200


class StudentApplyAPI(Resource):
    @auth_required('token')
    @roles_accepted('student')
    def post(self):
        """Apply to a drive/job"""
        data = request.get_json()
        drive_id = data.get('drive_id') or data.get('job_id')
        
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return {"message": "Student profile not found"}, 404
        
        success, msg = StudentService.apply_for_job(student.studentid, drive_id)
        return ({"message": msg}, 201) if success else ({"message": msg}, 400)