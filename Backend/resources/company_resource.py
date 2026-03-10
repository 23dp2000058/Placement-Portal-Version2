from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_accepted, current_user
from services.company_service import CompanyService
from models import Company

class CompanyProfile(Resource):
    # Only authenticated users with the 'company' role can access this
    method_decorators = [auth_required(), roles_accepted('company')]

    def get(self):
        """Fetch the current company profile details"""
        company = Company.query.filter_by(user_id=current_user.id).first()
        if not company:
            return {"message": "Company profile not found"}, 404
        
        return {
            "companyid": company.companyid,
            "name": company.name,
            "email": current_user.email,
            "industry": company.industry,
            "location": company.location,
            "description": company.description,
            "weblink": company.weblink,
            "HR_contact": company.HR_contact,
            "logo_url": company.logo_url,
            "is_approved": company.is_approved
        }, 200

    def put(self):
        """Update the company profile details"""
        data = request.get_json()
        
        # Call the service to handle the update
        # Call it through the class name
        success, message = CompanyService.update_company_profile(current_user.id, data)
        
        if not success:
            return {"message": message}, 400
            
        return {"message": message}, 200

class CompanyDashboard(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def get(self):
        # 1. Gate Access
        is_approved = CompanyService.check_approval_status(current_user.id)
        if not is_approved:
            return {
                "access": False,
                "message": "Admin approval pending",
                "status": "pending"
            }, 200

        company = CompanyService.get_company_by_user(current_user.id)
        applicants = CompanyService.get_applicants_for_company(company.companyid)
        
        return {
            "access": True,
            "company_name": company.name,
            "applicants": [{
                "application_id": a.applicationid,
                "student_name": a.student.name,
                "job_title": a.job.title,
                "status": a.application_status,
                "interview_date": a.interview_date.strftime("%Y-%m-%d %H:%M") if a.interview_date else None,
                "feedback": a.feedback
            } for a in applicants]
        }, 200

class CompanyApplicationAction(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def post(self, application_id):
        # 1. Check if the company is approved before allowing any action
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403

        # 2. Get the JSON data containing status, feedback, and/or offer_letter_link
        data = request.get_json() or {}
        
        # 3. Pass everything to a single service method for efficiency
        success, msg = CompanyService.process_application_action(
            application_id=application_id,
            status=data.get('status'),
            feedback=data.get('feedback'),
            interview_date=data.get('interview_date'),
            offer_link=data.get('offer_letter_link') # Using the Drive link strategy
        )

        return {"message": msg}, 200 if success else 400
    
class CompanyDrivesAPI(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def post(self):
        """Create a new placement drive (with an initial job) for this company."""
        # guard that only approved companies can create drives
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403

        data = request.get_json() or {}
        required_fields = ['date', 'title', 'description', 'salary', 'location','skills','branches']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {"message": f"Missing data: {', '.join(missing_fields)}"}, 400

        success, msg = CompanyService.create_drive_with_job(current_user.id, data)
        return {"message": msg}, 201 if success else 400

    @auth_required('token')
    @roles_accepted('company')
    def get(self):
        """Get all drives created by this company"""
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403
        
        drives = CompanyService.get_company_drives(current_user.id)
        return drives, 200


class CompanyDriveStatusAPI(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def put(self, drive_id):
        """Update status of a drive (e.g. mark completed)"""
        data = request.get_json() or {}
        status = data.get('status')
        if not status:
            return {"message": "Missing status"}, 400
        success, msg = CompanyService.update_drive_status(current_user.id, drive_id, status)
        return {"message": msg}, 200 if success else 400


class CompanyApplicationsAPI(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def get(self):
        """Get all applications for this company"""
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403
        
        applications = CompanyService.get_company_applications(current_user.id)
        return applications, 200


class CompanyDeleteDriveAPI(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def delete(self, drive_id):
        """Delete a drive"""
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403
        
        if CompanyService.delete_drive(current_user.id, drive_id):
            return {"message": "Drive deleted successfully"}, 200
        return {"message": "Drive not found or access denied"}, 404


class CompanyUpdateApplicationStatusAPI(Resource):
    @auth_required('token')
    @roles_accepted('company')
    def put(self, application_id):
        """Update application status"""
        if not CompanyService.check_approval_status(current_user.id):
            return {"message": "Access restricted until Admin approval"}, 403
        
        data = request.get_json()
        success, msg = CompanyService.update_application_status(current_user.id, application_id, data.get('status'))
        return ({"message": msg}, 200) if success else ({"message": msg}, 400)