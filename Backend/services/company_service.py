import os
from flask import current_app 
from extensions import db
from models import Application, Jobposition, Company, Placementdrive
from datetime import datetime

class CompanyService:
    @staticmethod
    def get_company_by_user(user_id):
        return Company.query.filter_by(user_id=user_id).first()

    @staticmethod
    def check_approval_status(user_id):
        company = Company.query.filter_by(user_id=user_id).first()
        # Ensure company exists, is approved, and the user account is active
        if company:
           return company.is_approved
        return False

    @staticmethod
   
    def create_drive_with_job(user_id, data):
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return False, "Company profile not found"

        # 1. GLOBAL CHECK: Ensure no other company is booked for this date
        target_date = datetime.strptime(data['date'], '%Y-%m-%d')
        existing_drive = Placementdrive.query.filter_by(drivedate=target_date).first()

        if existing_drive:
            # Fetch the name of the company already booked for clarity
            booked_company = Company.query.filter_by(companyid=existing_drive.companyid).first()
            company_name = booked_company.name if booked_company else "Another company"
            
            return False, f"Date Conflict: {data['date']} is already booked by {company_name}."

        try:
            # 1. Format the date for the ID
            # Converts "2026-04-15" to "20260415"
            date_str = data['date'].replace('-', '')
            
            # 2. Generate the Drive ID
            new_drive_id = f"DRV-{date_str}-{datetime.now().strftime('%f')}"

            # 3. Generate the Job ID with the Drive Date
            # Example: JOB-20260415-882341
            new_job_id = f"JOB-{date_str}-{datetime.now().strftime('%f')}"

            new_drive = Placementdrive(
                driveid=new_drive_id,
                companyid=company.companyid,
                drivedate=datetime.strptime(data['date'], '%Y-%m-%d'),
                driveapprovalstatus='inactive'
            )

            new_job = Jobposition(
                jobid=new_job_id, # Custom generated ID
                parentdrive=new_drive, 
                companyid=company.companyid,
                title=data.get('title'),
                job_description=data.get('description'),
                salary=data.get('salary'),
                skills_required=data.get('skills'),
                eligible_branches=data.get('branches'),
                job_location=data.get('location'),
            )

            db.session.add(new_drive)
            db.session.add(new_job)
            db.session.commit()
            
            return True, f"Success! Job created with ID: {new_job_id}"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    @staticmethod
    def get_applicants_for_company(company_id_str):
        return Application.query.join(Jobposition).filter(Jobposition.companyid == company_id_str).all()


    @staticmethod
    def update_company_profile(user_id, data):
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return False, "Company profile not found"

        # Update basic and branding details
        company.name = data.get('name', company.name)
        company.industry = data.get('industry', company.industry)
        company.location = data.get('location', company.location)
        company.description = data.get('description', company.description)
        company.logo_url = data.get('logo_url', company.logo_url)
        company.weblink = data.get('weblink', company.weblink)
        company.HR_contact = data.get('HR_contact', company.HR_contact)

        try:
            db.session.commit()
            return True, "Profile updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def _parse_interview_dt(s: str):
        # accepts `DD-MM-YYYY HH:MM`, `DD-MM-YYYY HH:MM:SS`, or `DD-MM-YYYYTHH:MM[:SS]`
        s = s.replace('T', ' ')
        for fmt in ('%d-%m-%Y %H:%M:%S', '%d-%m-%Y %H:%M'):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError("Invalid date format. Please use DD-MM-YYYY HH:MM or add :SS")

    @staticmethod
    def process_application_action(application_id, status=None, feedback=None, interview_date=None, offer_link=None):
        app = Application.query.filter_by(applicationid=application_id).first()
        if not app:
            return False, "Application not found"

        if status:
            app.application_status = status
        if feedback:
            app.feedback = feedback

        if interview_date:
            try:
                app.interview_date = CompanyService._parse_interview_dt(interview_date)
                app.application_status = 'Interview Scheduled'
            except ValueError as e:
                return False, str(e)

        if offer_link:
            app.offer_letter_path = offer_link
            app.application_status = 'Selected'
        try:
            db.session.commit()
            return True, "Application updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"

    @staticmethod
    def get_company_drives(user_id):
        """Get all drives created by a company"""
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return []
        
        drives = Placementdrive.query.filter_by(companyid=company.companyid).all()
        
        results = []
        for drive in drives:
            job_count = len(drive.jobs_offered) if drive.jobs_offered else 0
            app_count = Application.query.filter(
                Jobposition.drive_id == drive.driveid
            ).count()
            
            results.append({
                "id": drive.driveid,
                "name": drive.jobs_offered[0].title if drive.jobs_offered else "Job Drive",
                "date": drive.drivedate.strftime("%Y-%m-%d"),
                "position": drive.jobs_offered[0].title if drive.jobs_offered else "N/A",
                "status": drive.driveapprovalstatus,
                "applicant_count": app_count,
                "location": drive.jobs_offered[0].job_location if drive.jobs_offered else "N/A",
                "package": float(drive.jobs_offered[0].salary) if drive.jobs_offered and drive.jobs_offered[0].salary else 0
            })
        
        return results

    @staticmethod
    def get_company_applications(user_id):
        """Get all applications for jobs posted by this company"""
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return []
        
        applications = (
            Application.query
                .join(Jobposition, Application.jobid == Jobposition.jobid)
                .filter(Jobposition.companyid == company.companyid)
                .all()
        )
        
        results = []
        for app in applications:
            results.append({
                "id": app.applicationid,
                "drive_id": app.job.drive_id if app.job else None,
                "student_name": app.student.name if app.student else "Unknown",
                "student_email": app.student.user.email if app.student and app.student.user else "Unknown",
                "drive_name": app.job.title if app.job else "Unknown",
                "position": app.job.title if app.job else "Unknown",
                "status": app.application_status,
                "applied_date": app.applied_at.strftime("%Y-%m-%d") if app.applied_at else None,
                "interview_date": app.interview_date.strftime("%Y-%m-%d %H:%M") if app.interview_date else None,
                "feedback": app.feedback
            })
        
        return results

    @staticmethod
    def delete_drive(user_id, drive_id):
        """Delete a drive and associated jobs/applications"""
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return False
        
        drive = Placementdrive.query.filter_by(driveid=drive_id, companyid=company.companyid).first()
        if not drive:
            return False
        
        try:
            # Delete associated applications
            Application.query.filter_by(drive_id=drive_id).delete()
            # Delete associated jobs
            Jobposition.query.filter_by(drive_id=drive_id).delete()
            # Delete drive
            db.session.delete(drive)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    @staticmethod
    def update_drive_status(user_id, drive_id, new_status):
        """Change a drive's approval/status (e.g. mark closed) by its owner"""
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return False, "Company not found"

        drive = Placementdrive.query.filter_by(driveid=drive_id, companyid=company.companyid).first()
        if not drive:
            return False, "Drive not found or access denied"

        drive.driveapprovalstatus = new_status
        try:
            db.session.commit()
            return True, "Status updated"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def update_application_status(user_id, application_id, status):
        """Update application status by company"""
        company = Company.query.filter_by(user_id=user_id).first()
        if not company:
            return False, "Company not found"
        
        app = Application.query.filter_by(applicationid=application_id).first()
        if not app or app.company_id != company.companyid:
            return False, "Application not found or access denied"
        
        try:
            app.application_status = status
            db.session.commit()
            return True, "Status updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
