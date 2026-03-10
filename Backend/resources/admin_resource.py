from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted
from flask import jsonify, request
from services.admin_service import AdminService


class CompanyApprovalAPI(Resource):

    method_decorators = [auth_required('token'), roles_accepted('admin')]

    def put(self, **kwargs): 
        company_id = kwargs.get('company_id')
        
        # AdminService.approve_company only returns a True/False
        success = AdminService.approve_company(company_id)
        
        if success:
            # We provide our own success message here
            return {"message": "Company approved successfully"}, 200
        
        # And our own error message here
        return {"message": "Approval failed", "error": "Company not found or already approved"}, 400


class BlacklistResource(Resource):
    def post(self, entity_type, entity_id):
        """
        flask-restful automatically maps this to the POST method.
        """
        data = request.get_json() or {}
        status = data.get('status', True)

        # Call the service logic
        success, message = AdminService.blacklist_update_status(entity_type, entity_id, status)

        if success:
            return {"message": message}, 200
        return {"message": message}, 400


class AdminSearch(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self, target):

        q = request.args.get('q')

        if target == 'company':
            results = AdminService.search_companies(name=q)

            return jsonify([{
                "id": c.companyid,
                "name": c.name,
                "industry": c.industry,
                "approved": c.is_approved,
                "logo": c.logo_url
            } for c in results])

        if target == 'student':
            results = AdminService.search_students(q)

            return jsonify([{
                "id": s.studentid,
                "name": s.name,
                "branch": s.branch,
                "cgpa": s.cgpa,
                "email": s.user.email
            } for s in results])


class AdminApplicationMonitoring(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):

        return jsonify(AdminService.get_all_applications())


class AdminCompaniesResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        """Get all registered companies"""
        companies = AdminService.get_all_companies()
        return jsonify(companies)


class AdminStudentsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        """Get all registered students"""
        students = AdminService.get_all_students()
        return jsonify(students)


class AdminCompanyApplicationsResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def get(self):
        """Get pending company applications"""
        pending_apps = AdminService.get_pending_company_applications()
        return jsonify(pending_apps)


class AdminCompanyDeleteResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def delete(self, company_id):
        """Delete a company"""
        if AdminService.delete_company(company_id):
            return {"message": "Company deleted successfully"}, 200
        return {"message": "Company not found"}, 404


class AdminStudentDeleteResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def delete(self, student_id):
        """Delete a student"""
        if AdminService.delete_student(student_id):
            return {"message": "Student deleted successfully"}, 200
        return {"message": "Student not found"}, 404


class AdminCompanyApproveResource(Resource):
    @auth_required('token')
    @roles_required('admin')
    def post(self, application_id):
        """Approve a pending company application"""
        if AdminService.approve_company(application_id):
            return {"message": "Company approved successfully"}, 200
        return {"message": "Company not found"}, 404
