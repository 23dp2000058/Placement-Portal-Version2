import os
from flask import current_app
from extensions import db
from models import Student, Application, Jobposition, Placementdrive, Company
from datetime import datetime
from werkzeug.utils import secure_filename

class StudentService:
    @staticmethod
    def get_jobs_with_status(student_id_str):
        """Fetch active jobs ONLY from approved companies"""
        # Join with Company to check is_approved status
        
        all_jobs = (
            Jobposition.query
                .join(Jobposition.company)
                .join(Placementdrive, Jobposition.drive_id == Placementdrive.driveid)
                .filter(
                    Jobposition.company.has(is_approved=True),
                    Placementdrive.driveapprovalstatus == 'approved'
                )
                .all())
        student_apps = {a.jobid: a for a in Application.query.filter_by(studentid=student_id_str).all()}
        
        results = []
        for job in all_jobs:
            app = student_apps.get(job.jobid)
            results.append({
                "job_id": job.jobid,
                "title": job.title,
                "company": job.company.name,
                "salary": job.salary, 
                "applied_status": app.application_status if app else "Not Applied",
                "location": job.job_location, 
                "description": job.job_description,
                "eligible_branches": job.eligible_branches,
                "interview_date": app.interview_date.strftime("%Y-%m-%d %H:%M") if app and app.interview_date else None,
                "feedback": app.feedback if app else None
            })
        return results
    @staticmethod
    def update_student_profile(user_id, data):
            student = Student.query.filter_by(user_id=user_id).first()
            if not student:
                return False, "Student not found"

            # Update the existing text and link columns
            student.skills = data.get('skills', student.skills)
            student.education_history = data.get('education_history', student.education_history)
            student.resume_link = data.get('resume_link', student.resume_link) 
            
            db.session.commit()
            return True, "Profile updated with Drive link!"
    @staticmethod
    def apply_for_job(student_id_str, job_id_str):
        """Logic for job applications including branch and blacklist checks"""
        student = Student.query.filter_by(studentid=student_id_str).first()
        job = Jobposition.query.filter_by(jobid=job_id_str).first()

        if not student:
            return False, "Student record not found"
        if not job:
            return False, "Job not found"

        # 1. Branch Validation
        if job.eligible_branches and job.eligible_branches != "All":
            allowed_list = [b.strip() for b in job.eligible_branches.split(',')]
            if student.branch not in allowed_list:
                return False, f"Not eligible. Open to: {job.eligible_branches}"

        # 2. Blacklist Check
        if student.is_blacklisted:
            return False, "You are blacklisted from placements."

        # 3. Duplicate Application Check
        existing = Application.query.filter_by(
            studentid=student_id_str, 
            jobid=job_id_str
        ).first()
        
        if existing:
            return False, "Already applied for this position."

        # 4. Create Application
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_id = f"APP-{student_id_str}-{timestamp}" 

            new_app = Application(
                applicationid=unique_id,
                jobid=job_id_str,
                studentid=student_id_str,
                application_status="Applied",
                drive_id=job.drive_id,      # Links directly to the drive
                company_id=job.companyid
            )
            db.session.add(new_app)
            db.session.commit()
            return True, "Applied successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"

    @staticmethod
    def get_placement_history(student_id_str):
        """Retrieve all previous applications for the student"""
        history = Application.query.filter_by(studentid=student_id_str).all()
        
        return [{
            "company": h.job.company.name if h.job and h.job.company else "Unknown",
            "role": h.job.title if h.job else "Unknown",
            "status": h.application_status,
            "date": h.applied_at.strftime("%Y-%m-%d") if h.applied_at else "N/A",
            "feedback": h.feedback or "No feedback yet"
        } for h in history]

    @staticmethod
    def get_student_profile(user_id):
        """Get student profile by user_id"""
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return None
        return {
            "id": student.studentid,
            "name": student.name,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "year": student.year,
            "email": student.user.email if student.user else "",
            "skills": student.skills,
            "resume_link": student.resume_link
        }

    @staticmethod
    def get_available_drives(student_id_str):
        """Get all available drives for student (with job info)"""
        student = Student.query.filter_by(studentid=student_id_str).first()
        if not student:
            return []
        
        # Get all approved jobs from approved companies with approved drives
        jobs = (
            Jobposition.query
                .join(Jobposition.company)
                .join(Placementdrive, Jobposition.drive_id == Placementdrive.driveid)
                .filter(
                    Jobposition.company.has(is_approved=True),
                    Placementdrive.driveapprovalstatus == 'approved'
                )
                .all()
        )
        
        # Get all jobs for student with applied status
        student_apps = {a.jobid: a for a in Application.query.filter_by(studentid=student_id_str).all()}
        
        results = []
        for job in jobs:
            app = student_apps.get(job.jobid)
            results.append({
                "id": job.jobid,
                "drive_id": job.drive_id,
                "company_name": job.company.name,
                "position": job.title,
                "package": float(job.salary) if job.salary else 0,
                "location": job.job_location,
                "description": job.job_description,
                "status": "applied" if app else "available"
            })
        return results

    @staticmethod
    def get_applied_drives(student_id_str):
        """Get drives student has already applied to"""
        applications = Application.query.filter_by(studentid=student_id_str).all()
        
        results = []
        for app in applications:
            if app.job:
                results.append({
                    "id": app.job.jobid,
                    "application_id": app.applicationid,
                    "company_name": app.job.company.name,
                    "position": app.job.title,
                    "applied_date": app.applied_at.strftime("%Y-%m-%d") if app.applied_at else None,
                    "status": app.application_status
                })
        return results

    @staticmethod
    def check_if_applied(student_id_str, job_id_str):
        """Check if student has already applied to a job"""
        app = Application.query.filter_by(
            studentid=student_id_str,
            jobid=job_id_str
        ).first()
        return app is not None

    @staticmethod
    def get_application_history(student_id_str):
        """Get detailed application history with all relevant info"""
        applications = Application.query.filter_by(studentid=student_id_str).all()
        
        results = []
        for app in applications:
            if app.job and app.job.company:
                results.append({
                    "id": app.applicationid,
                    "drive_name": app.job.title,
                    "company": app.job.company.name,
                    "applied_date": app.applied_at.strftime("%Y-%m-%d") if app.applied_at else None,
                    "status": app.application_status,
                    "result": app.feedback or "Pending",
                    "interview_date": app.interview_date.strftime("%Y-%m-%d %H:%M") if app.interview_date else None
                })
        return results